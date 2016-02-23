import re
import json
from random import choice
from os.path import join as joinpath
from zope.interface import implementer

from redlib.api.system import *
from redlib.api.web import HtmlParser

from ..web import func as webfunc
from ..util import log, Retry
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

	search_url 			= "http://imgur.com/search/score/all?"
	search_result_link_prefix 	= "http://imgur.com"
	imgur_base_url_regex 		= re.compile('https?://imgur.com/(.*)')
	imgur_gallery_base_url 		= 'http://imgur.com/gallery/'
	image_div_img_url_prefix 	= 'http:'

	def __init__(self):
		super(Imgur, self).__init__()

		config = Config()
		self.get_full_album = config.get('imgur.get_full_album')


	def get_image_url(self, query=None, color=None):
		if self.image_urls_available():
			image_url = self.select_url()
			return image_url

		image_url = None
		search = album = False

		if query is not None:
			search = True
			album = False
		else:
			search = choice([True, False])
			album = not search

		try:
			if search:
				image_url = self.get_image_url_from_search(query)
			elif album:
				image_url = self.get_image_url_from_random_album()
		except ImgurError as e:
			log.error(str(e))

		return image_url


	def get_image_url_from_search(self, query):
		results = self.search(query)

		page_url = self.search_result_link_prefix + choice(results)
		self.add_trace_step('selected page', page_url)

		log.debug('selected page url: ' + page_url)

		image_url = self.get_image_url_from_page(page_url)
		return image_url


	def get_image_url_from_random_album(self):
		album_url = ImgurAlbumList().get_random()

		self.add_trace_step('selected random album', album_url)

		image_url = self.get_image_url_from_page(album_url)
		return image_url


	def get_image_url_from_page(self, page_url):
		match = self.imgur_base_url_regex.match(page_url)
		if match is None:
			raise ImgurError('invalid imgur url: %s'%page_url)

		etree = self.get_etree(self.get_page_html(page_url))

		image_div_path = './/div[@class=\'post-image\']'
		image_divs = etree.findall(image_div_path)
		
		image_urls = self.get_urls_from_image_divs(image_divs)
		self.extract_title(etree)	
		self.extract_username(etree)

		if len(image_urls) == 1 :				#single image found
			log.debug('found 1 image on page')
			self.add_trace_step('found one image', image_urls[0])
			self.add_url(image_urls[0], self._image_context)
			return image_urls[0]

		else:							#multiple images found
			trunc_div = etree.find(".//a[@class='post-loadall']")
			if trunc_div == None or not self.get_full_album:		#don't get full album
				self.add_urls(image_urls)
				return self.select_url()

			else:								#get full album
				page_id = page_url[page_url.rfind('/') + 1 : ]
				full_album_url = 'http://imgur.com/a/%s/layout/grid'%page_id

				log.debug('imgur: getting full album, %s'%full_album_url)
				return self.get_url_from_full_album(full_album_url)

		return None


	def extract_username(self, etree):
		username = None

		a = etree.findall(".//a[@class='post-account']")
		if len(a) > 0 :
			self._image_context.artist = a[0].text.strip()
			return

		log.debug('username not found')


	def extract_title(self, etree):
		title_h1 = etree.findall(".//div[@id='post-title-container']/h1")

		if len(title_h1) > 0 :
			self._image_context.title = title_h1[0].text
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
				image_urls.append(self.image_div_img_url_prefix + img.attrib['src'])

		if len(image_urls) == 0 :
			log.error('no images found on page')
			raise ServiceError()

		return image_urls


	def get_url_from_full_album(self, full_album_url):
		html = self.get_page_html(full_album_url)

		images_regex = re.compile("images\s+:\s+({.*})")
		matches = images_regex.findall(html)

		urls = []
		if matches is not None and len(matches) == 1:
			images_data = json.loads(matches[0])
			for item in images_data['images']:
				urls.append('http://i.imgur.com/%s%s'%(item['hash'], item['ext']))
		else: 
			raise ImgurError("cannot find images data on full album")
		
		self.add_urls(urls)
		return self.select_url()

	
	def search(self, query):
		if query is None:
			query = SearchTermList().get_random()
			self.add_trace_step('random search term', query)

		qs = {
			'q_size_px'	: 'med',
			'q_size_mpx'	: 'med',
			'q_type'	: 'jpg',
			'q_all'		: query
		}

		url = self.search_url + urlencode(qs)
		res = webfunc.get_page(url)

		import pdb; pdb.set_trace()
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

