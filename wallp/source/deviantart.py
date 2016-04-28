from random import choice
import xml.etree.ElementTree as ET

from redlib.api.system import *
from redlib.api.web import HtmlStripper
from six.moves.urllib.parse import urlencode

from ..util.logger import log
from ..desktop import get_desktop, get_standard_desktop_size
from ..db.app.query_list import QueryList
from .base import SourceError, SourceParams, Source
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from .image import Image


class DeviantArtParams(SourceParams):
	name = 'deviantart'

	def __init__(self, query=None):
		self.query = query

		self.hash_params = ['query']


class DeviantArt(Source):
	name = 'deviantart'
	params_cls = DeviantArtParams

	rss_url_base = 'http://backend.deviantart.com/rss.xml?type=deviation&order=11&boost:popular&'
	xmlns = {'media': 'http://search.yahoo.com/mrss/'}


	def __init__(self):
		self._http = HttpHelper()
		self._trace = Trace()


	def get_image(self, params=None):
		params = params or DeviantArtParams()

		self._images = Images(params, cache=True, cache_timeout='1d', trace=self._trace)

		if not self._images.available():
			self.search(params)

		return self._http.download_image(self._images, self._trace)


	def search(self, params):
		if params.query is None:
			params.query = QueryList().random()
			self._trace.add_step('random search', params.query)
		else:
			self._trace.add_step('search', params.query)

		search_url = self.make_search_url(params.query)
		response = self._http.get(search_url, msg='searching deviantart')
		self.parse_search_response(response)
	

	def make_search_url(self, query):
		params = {}
		params['q'] = query

		width, height = get_desktop().get_size()
		width, height = get_standard_desktop_size(width, height)

		params['q'] += ' width:' + str(width) + ' height:' + str(height)

		url = self.rss_url_base + urlencode(params)
		log.debug('deviantart rss url: ' + url)

		return url


	def parse_search_response(self, xml):
		rss = ET.fromstring(xml)

		for item in rss.findall('./channel/item', self.xmlns):
			mr = item.findall('media:rating', self.xmlns)[0]
			if mr.text == 'nonadult':
				mc = item.findall('media:content', self.xmlns)
				if len(mc) == 0:
					continue
				mc = mc[0]

				image = Image()

				image.url = mc.get('url')
				image.width = int(mc.get('width') or 0) 
				image.height = int(mc.get('height') or 0)
				self.add_image_context(image, item)

				self._images.add(image)

		log.debug('got %d results'%self._images.count)


	def add_image_context(self, image, item):
		def extract_field(name):
			field = item.findall(name, self.xmlns)
			if len(field) > 0:
				return field[0].text
			else:
				return None

		image.user 		= extract_field('media:credit')
		image.title 		= extract_field('title')
		image.context_url	= extract_field('link')

		description = extract_field('description')
		parser = HtmlStripper()
		parser.feed(description)
		description = parser.get_output() 

		image.description = description


	def get_trace(self):
		return self._trace.steps

