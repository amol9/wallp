import re
import json
from random import choice
from os.path import join as joinpath
from zope.interface import implementer

from mutils.system import *
from mutils.html.parser import HtmlParser

from .. import web
from ..util.logger import log
from .service import IHttpService, ServiceError
from .image_info_mixin import ImageInfoMixin

if is_py3():
	from urllib.parse import urlencode
else:
	from urllib import urlencode


@implementer(IHttpService)
class Imgur(ImageInfoMixin):
	name = 'imgur'

	search_url = "http://imgur.com/search?"
	search_result_link_prefix = "http://imgur.com"
	imgur_base_url_regex = re.compile('https?://imgur.com/(.*)')
	imgur_gallery_base_url = 'http://imgur.com/gallery/'

	def __init__(self):
		super(Imgur, self).__init__()
		self.get_full_album = True


	def get_image_url(self, query=None, color=None):
		image_url = None
		search = album = False

		if query is not None:
			search = True
			album = False
		else:
			search = choice([True, False])
			album = not search

		if search:
			image_url = self.get_image_url_from_search(query)
		elif album:
			image_url = self.get_image_url_from_random_album()
	
		return image_url


	def get_image_url_from_search(self, query):
		assert query

		results = self.search(query)
		self.add_trace('searched imgur', query)

		page_url = self.search_result_link_prefix + results[choice(results)]
		self.add_trace('selected page from results', page_url)

		log.debug('selected page url: ' + page_url)

		image_url, _ = self.get_image_url_from_page(page_url)
		return image_url


	def get_image_url_from_random_album(self):
		album_url = ImgurAlbumList().get_random()

		self.add_trace('selected random album', album_url)

		image_url, _ = self.get_image_url_from_page(album_url)
		return image_url


	def get_image_url_from_page(self, page_url):
		match = self.imgur_base_url_regex.match(page_url)
		if match is None:
			raise ImgurError('invalid imgur url: %s'%page_url)

		section = match.group(1)

		if section.startswith('a/'):
			url, image_count = self.get_url_from_full_album(page_url)
		elif section.startswith('gallery'):
			url, image_count = self.get_url_from_gallery_link(page_url)
		else:
			url, image_count = self.get_url_from_direct_link(page_url)

		log.debug('imgur: selected url = %s'%url)

		if not url.startswith('http'):
			url = 'http' + url

		return url, image_count


	def get_url_from_gallery_link(self, page_url):
		image_div_path = './/div[@class=\'left main-image\']' 	+ \
				 '/div[@class=\'panel\']' 		+ \
				 '/div[@id=\'image\']' 			+ \
				 '//div[@class=\'image textbox\']'

		return self.get_url(page_url, image_div_path)


	def get_url_from_direct_link(self, page_url):
		image_div_path = './/div[@class=\'left main-image\']'	+ \
				'/div[@class=\'panel\']' 		+ \
				 '//div[@class=\'image textbox\']'

		return self.get_url(page_url, image_div_path)


	def extract_username(self, etree):
		username = None

		a = etree.findall(".//p[@class='under-title-info']//a")
		if len(a) > 0:
			href = a[0].attrib['href']
			username = href[href.rfind('/') + 1 : ]
			self._image_source.artist = username
			return

		a = etree.findall(".//div[@class='under-title-info']//a")
		if len(a) > 0:
			username = a[0].text
			self._image_source.artist = username
			return


	def get_url(self, page_url, image_div_path):		
		html = web.func.get_page(page_url)
		parser = HtmlParser(skip_tags=['head'])
		parser.feed(html)
		etree = parser.etree

		image_divs = etree.findall(image_div_path)

		title_h1 = etree.findall('.//h1[@id=\'image-title\']')	#gallery, direct link

		if len(title_h1) > 0:
			self._image_source.title = title_h1[0].text
		else:
			log.debug('title h1 not found')

		self.extract_username(etree)

		image_count = None

		if len(image_divs) == 0:
			log.error('can\'t find main div on imgur page')
			raise ServiceError()

		if len(image_divs) == 1:
			log.debug('imgur: 1 image on page')
			img = image_divs[0].find('.//img')
			if img is not None:
				url = img.attrib['src']
				image_count = 1
			else:
				raise ServiceError()
		else:
			url = None
			trunc_div = etree.find('.//div[@id=\'album-truncated\']')
			if trunc_div == None or self.get_full_album == False:
				urls = []
				for div in image_divs:
					img = div.find('.//img')
					if img is not None:
						urls.append(img.attrib['src'])

				log.debug('imgur: %d urls found'%len(urls))
				if len(urls) == 0:
					raise ServiceError()

				url = choice(urls)
				image_count = len(urls)
			else:
				page_id = page_url[page_url.rfind('/')+1:]
				full_album_url = 'http://imgur.com/a/%s?gallery'%page_id

				log.debug('imgur: getting full album, %s'%full_album_url)
				url, image_count = self.get_url_from_full_album(full_album_url)

		#self._image_trace.append(ImageTrace(name='get random url from gallery', data=url))
		return url, image_count
	

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
		#log.testresult(len(urls))

		url = choice(urls)
		image_count = len(urls)

		#self._image_trace.append(ImageTrace(name='get random url from full album', data=url))
		return url, image_count

	
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

		url = self.search_url + urlencode(qs)
		res = web.func.get_page(url)

		link_regex = re.compile("<a.*?class=\"image-list-link\".*?href=\"(.*?)\"")
		matches = link_regex.findall(res)

		link_urls = []
		if matches:
			for m in matches:
				link_urls.append(m)

		#self._image_trace.append(ImageTrace(name='imgur search', data=query))
		return link_urls

