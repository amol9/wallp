from random import choice
import xml.etree.ElementTree as ET
from zope.interface import implementer

from mutils.system import *

from .. import web
from ..util.logger import log
from .service import IHttpService, ServiceError
from ..desktop import get_desktop, get_standard_desktop_size
from .image_mixin import ImageMixin
from ..db import SearchTermList

if is_py3():
	from urllib.parse import urlencode
else:
	from urllib import urlencode


@implementer(IHttpService)
class DeviantArt(ImageMixin):
	name = 'deviantart'
	rss_url_base = 'http://backend.deviantart.com/rss.xml?type=deviation&order=11&boost:popular&'
	xmlns = {'media': 'http://search.yahoo.com/mrss/'}

	def __init__(self):
		super(DeviantArt, self).__init__()


	def get_image_url(self, query=None, color=None):
		search_url = self.get_search_url(query)
		response = web.func.get_page(search_url)
	
		image_urls = self.get_image_url_list(response)
		
		image_url = choice(image_urls)
		self.add_trace_step('selected random url', image_url)
		log.info('deviantart selected url: ' + image_url)

		return image_url


	def get_search_url(self, query):
		if query is None:
			query = SearchTermList().get_random()
	
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

		image_urls = []
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
					image_urls.append(mc.get('url'))

		self.add_trace_step('got %d results'%len(image_urls), None)
		return image_urls

