import re
import json
from random import choice
from os.path import join as joinpath
from zope.interface import implementer

from mutils.system import *
from mutils.html.parser import HtmlParser

from ..web import func as webfunc
from ..util.logger import log
from .service import IHttpService, ServiceError
from .image_info_mixin import ImageInfoMixin
from .image_urls_mixin import ImageUrlsMixin
from ..db import Config, ImgurAlbumList, SearchTermList

if is_py3():
	from urllib.parse import urlencode
else:
	from urllib import urlencode


class ImgurError(Exception):
	pass


@implementer(IHttpService)
class Imgur(ImageInfoMixin, ImageUrlsMixin):
	name = 'imgur'

	search_url = "http://imgur.com/search?"
	search_result_link_prefix = "http://imgur.com"
	imgur_base_url_regex = re.compile('https?://imgur.com/(.*)')
	imgur_gallery_base_url = 'http://imgur.com/gallery/'

	def __init__(self):
		super(Imgur, self).__init__()

		config = Config()
		self.get_full_album = config.get('imgur.get_full_album')


	def get_image_url(self, query=None, color=None):
		image_url = None
		search = album = False

		if query is not None:
			search = True
			album = False
		else:
			search = choice([True, False])
			album = not search

		retry = Retry(retries=3, final_exc=ServiceError())
		while retry.left():
			try:
				if search:
					image_url = self.get_image_url_from_search(query)
				elif album:
					image_url = self.get_image_url_from_random_album()
				retry.cancel()
			except ImgurError as e:
				log.error(str(e))
				retry.retry()
	
		return image_url


	def get_image_url_from_search(self, query):
		results = self.search(query)

		page_url = self.search_result_link_prefix + choice(results)
		self.add_trace_step('selected page from results', page_url)

		log.debug('selected page url: ' + page_url)

		image_url, _ = self.get_image_url_from_page(page_url)
		return image_url


	def get_image_url_from_random_album(self):
		album_url = ImgurAlbumList().get_random()

		self.add_trace_step('selected random album', album_url)

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

		return self.get_url_from_link(page_url, image_div_path)


	def get_url_from_direct_link(self, page_url):
		image_div_path = './/div[@class=\'left main-image\']'	+ \
				'/div[@class=\'panel\']' 		+ \
				 '//div[@class=\'image textbox\']'

		return self.get_url_from_link(page_url, image_div_path)


	def get_url_from_link(self, page_url, image_div_path):
		etree = self.get_etree(self.get_page_html(page_url))

		image_divs = etree.findall(image_div_path)
		
		image_urls = self.get_urls_from_image_divs(image_divs)
		self.extract_title(etree)	
		self.extract_username(etree)

		if len(image_urls) == 1 :				#single image found
			log.debug('found 1 image on page')
			return image_urls[0], 1

		else:							#multiple images found
			trunc_div = etree.find('.//div[@id=\'album-truncated\']')
			if trunc_div == None or not self.get_full_album:		#don't get full album
				return self.select_url(image_urls)

			else:								#get full album
				page_id = page_url[page_url.rfind('/') + 1 : ]
				full_album_url = 'http://imgur.com/a/%s?gallery'%page_id

				log.debug('imgur: getting full album, %s'%full_album_url)
				return self.get_url_from_full_album(full_album_url)

		return None, None


	def extract_username(self, etree):
		username = None

		a = etree.findall(".//p[@class='under-title-info']//a")
		if len(a) > 0 :
			href = a[0].attrib['href']
			username = href[href.rfind('/') + 1 : ]
			self._image_source.artist = username
			return

		a = etree.findall(".//div[@class='under-title-info']//a")
		if len(a) > 0 :
			username = a[0].text
			self._image_source.artist = username
			return
		log.debug('username not found')


	def extract_title(self, etree):
		title_h1 = etree.findall('.//h1[@id=\'image-title\']')		#for gallery, direct link

		if len(title_h1) > 0 :
			self._image_source.title = title_h1[0].text
			return
		log.debug('title h1 not found')


	def get_etree(self, html):
		parser = HtmlParser(skip_tags=['head'])
		parser.feed(html)
		etree = parser.etree

		return etree


	def get_page_html(self, page_url):
		return webfunc.get_page(page_url)


	def get_urls_from_image_divs(self, image_divs):
		image_urls = []
		for div in image_divs:
			img = div.find('.//img')
			if img is not None:
				image_urls.append(img.attrib['src'])

		if len(image_urls) == 0 :
			log.error('no images found on page')
			raise ServiceError()

		return image_urls


	def get_url_from_full_album(self, full_album_url):
		html = self.get_page_html(full_album_url)

		layout_regex = re.compile("layout\s+:\s+\'g\'", re.M)
		match = layout_regex.findall(html)

		urls = []
		if match is None:		#normal album
			etree = self.get_etree(html)
			image_divs = etree.findall('.//div[@class=\'left main\']/div[@class=\'panel\']'
							'/div[@id=\'image-container\']//div[@class=\'image\']')

			for div in image_divs:
				a = div.find('.//a')
				if a is not None:
					urls.append(a.attrib['href'])

		else:				#really big album
			log.debug('really big album')
			images_regex = re.compile("images\s+:\s+({.*})", re.M)
			matches = images_regex.findall(html)

			if matches is not None:
				images_data = json.loads(matches[0])
				for item in images_data['items']:
					urls.append('//i.imgur.com/%s%s'%(item['hash'], item['ext']))
		
		return self.select_url(urls)

	
	def search(self, query):
		if query is None:
			query = SearchTermList().get_random()
		qs = {
			'q_size_px'	: 'med',
			'q_size_mpx'	: 'med',
			'q_type'	: 'jpg',
			'q_all'		: query
		}

		url = self.search_url + urlencode(qs)
		res = webfunc.get_page(url)

		link_regex = re.compile("<a.*?class=\"image-list-link\".*?href=\"(.*?)\"")
		matches = link_regex.findall(res)

		link_urls = []
		if matches is not None:
			for m in matches:
				link_urls.append(m)
		else:
			raise ImgurError('no search results for %s'%query)

		self.add_trace_step('searched imgur', query)
		log.debug('searched for: %s'%query)
		return link_urls

