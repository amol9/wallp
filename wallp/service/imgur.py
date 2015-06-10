import re
import json
from random import randint
from os.path import join as joinpath
from zope.interface import implementer

from mutils.system import *
from mutils.html.parser import HtmlParser

from .. import web
from ..util.logger import log
from .service import IHttpService, ServiceError
from .image_source import ImageSource
from ..db import ImageTrace
from .image_mixin import ImageMixin

if is_py3():
	from urllib.parse import urlencode
else:
	from urllib import urlencode


search_url = "http://imgur.com/search?"
search_result_link_prefix = "http://imgur.com"
get_full_album = True


@implementer(IHttpService)
class Imgur(ImageMixin):
	name = 'imgur'

	def __init__(self):
		super(Imgur, self).__init__()


	def get_image_url(self, query=None, color=None):
		return 'http://i.imgur.com/S9JMr.jpg'

		results = self.search(query)
		page_url = search_result_link_prefix + results[randint(0, len(results) - 1)]

		self._image_trace.append(ImageTrace(name='select random url', data=page_url))
		log.debug('selected page url: ' + page_url)
		
		image_url = self.get_image_url_from_page(page_url)
		'''ext = image_url[image_url.rfind('.')+1:]
		save_path = joinpath(pictures_dir, basename + '.' + ext)

		download(image_url, save_path)'''

		return image_url


	def get_image_url_from_page(self, page_url):
		if page_url.find('/a/') != -1:
			url = self.get_url_from_full_album(page_url)
		else:
			url = self.get_url_from_gallery(page_url)

		if not url.startswith('http'):
			url = 'http:' + url

		log.debug('imgur: selected url = %s'%url)
		return url


	def get_url_from_gallery(self, page_url):		
		html = web.func.get_page(page_url)
		parser = HtmlParser(skip_tags=['head'])
		parser.feed(html)
		etree = parser.etree

		image_divs = etree.findall('.//div[@class=\'left main-image\']/div[@class=\'panel\']'
						'/div[@id=\'image\']//div[@class=\'image textbox\']')

		#r = etree.findall('.//h1[@id=\'image-title\']')
		#self._image_source.title = r[0].text

		if len(image_divs) == 0:
			log.error('can\'t find main div on imgur page')
			raise ServiceError()

		if len(image_divs) == 1:
			log.debug('imgur: 1 image on page')
			img = image_divs[0].find('.//img')
			if img is not None:
				url = img.attrib['src']
				log.testresult(1)
			else:
				raise ServiceError()
		else:
			url = None
			trunc_div = etree.find('.//div[@id=\'album-truncated\']')
			if trunc_div == None or get_full_album == False:
				urls = []
				for div in image_divs:
					img = div.find('.//img')
					if img is not None:
						urls.append(img.attrib['src'])

				log.debug('imgur: %d urls found'%len(urls))
				log.testresult(len(urls))
				if len(urls) == 0:
					raise ServiceError()

				url = urls[randint(0, len(urls) - 1)]
			else:
				page_id = page_url[page_url.rfind('/')+1:]
				full_album_url = 'http://imgur.com/a/%s?gallery'%page_id

				log.debug('imgur: getting full album, %s'%full_album_url)
				url = self.get_url_from_full_album(full_album_url)

		self._image_trace.append(ImageTrace(name='get random url from gallery', data=url))
		return url
	

	def get_url_from_full_album(self, full_album_url):
		html = web.func.get_page(full_album_url)

		really_big_album = False
		layout_regex = re.compile("layout\s+:\s+\'g\'", re.M)
		match = layout_regex.findall(html)

		if match is not None:
			really_big_album = True

		urls = []
		if not really_big_album:
			parser = HtmlParser()
			parser.feed(html)
			etree = parser.etree

			image_divs = etree.findall('.//div[@class=\'left main\']/div[@class=\'panel\']'
							'/div[@id=\'image-container\']//div[@class=\'image\']')

			for div in image_divs:
				a = div.find('.//a')
				if a is not None:
					urls.append(a.attrib['href'])

		else:
			log.debug('really big album')
			images_regex = re.compile("images\s+:\s+({.*})", re.M)
			matches = images_regex.findall(html)

			if matches is not None:
				images_data = json.loads(matches[0])
				for item in images_data['items']:
					urls.append('//i.imgur.com/%s%s'%(item['hash'], item['ext']))
		
		log.debug('imgur: %d urls found'%len(urls))
		log.testresult(len(urls))
		url = urls[randint(0, len(urls) - 1)]

		self._image_trace.append(ImageTrace(name='get random url from full album', data=url))
		return url	

	
	def search(self, query=None):
		if not query:
			qs = {
				'q': 'wallpapers'
			}
		else:
			qs = {
				'q_size_px': 'med',
				'q_size_mpx': 'med',
				'q_type': 'jpg',
				'q_all': query
			}

		url = search_url + urlencode(qs)
		res = web.func.get_page(url)

		link_regex = re.compile("<a.*?class=\"image-list-link\".*?href=\"(.*?)\"")
		matches = link_regex.findall(res)

		link_urls = []
		if matches:
			for m in matches:
				link_urls.append(m)

		self._image_trace.append(ImageTrace(name='imgur search', data=query))
		return link_urls

