from random import choice
import xml.etree.ElementTree as ET
from zope.interface import implementer

from redlib.api.system import *
from redlib.api.web import HtmlStripper

from .. import web
from ..util.logger import log
from .service import IHttpService, ServiceError
from ..desktop import get_desktop, get_standard_desktop_size
from .image_info_mixin import ImageInfoMixin
from .image_urls_mixin import ImageUrlsMixin
from .image_context import ImageContext
from ..db import SearchTermList

if is_py3():
	from urllib.parse import urlencode
else:
	from urllib import urlencode


@implementer(IHttpService)
class DeviantArt(ImageInfoMixin, ImageUrlsMixin):
	name = 'deviantart'
	rss_url_base = 'http://backend.deviantart.com/rss.xml?type=deviation&order=11&boost:popular&'
	xmlns = {'media': 'http://search.yahoo.com/mrss/'}

	def __init__(self):
		super(DeviantArt, self).__init__()


	def get_image_url(self, query=None, color=None):
		if self.image_urls_available():
			image_url = self.select_url()
			return image_url

		search_url = self.get_search_url(query)
		response = web.func.get_page(search_url)
	
		self.get_image_url_list(response)
		
		image_url = self.select_url()
		return image_url


	def get_search_url(self, query):
		if query is None:
			query = SearchTermList().get_random()
			self.add_trace_step('random search term', query)
		else:
			self.add_trace_step('search term', query)
	
		params = {}
		params['q'] = query

		width, height = get_desktop().get_size()
		width, height = get_standard_desktop_size(width, height)

		params['q'] += ' width:' + str(width) + ' height:' + str(height)

		url = self.rss_url_base + urlencode(params)
		log.info('da rss url: ' + url)
		self.add_trace_step('searched deviantart', query)

		return url


	def get_image_url_list(self, xml):
		rss = ET.fromstring(xml)

		width, height = get_desktop().get_size()
		width, height = get_standard_desktop_size(width, height)

		for item in rss.findall('./channel/item', self.xmlns):
			mr = item.findall('media:rating', self.xmlns)[0]
			if mr.text == 'nonadult':
				mc = item.findall('media:content', self.xmlns)
				if len(mc) == 0:
					continue
				mc = mc[0]

				image_width = int(mc.get('width')) if mc.get('width') != None else 0
				image_height = int(mc.get('height')) if mc.get('height') != None else 0
				
				if (image_width >= width * 0.9) and (image_height >= height * 0.9):
					self.add_url(mc.get('url'), self.extract_image_context(item))

		log.debug('got %d results'%self.image_count)


	def extract_image_context(self, item):
		image_context = ImageContext()

		def extract_field(name):
			field = item.findall(name, self.xmlns)
			if len(field) > 0:
				return field[0].text
			else:
				return None

		image_context.artist 		= extract_field('media:credit')
		image_context.title 		= extract_field('title')
		image_context.url		= extract_field('link')

		description = extract_field('description')
		parser = HtmlStripper()
		parser.feed(description)
		description = parser.get_output() 
		image_context.description = description

		return image_context

