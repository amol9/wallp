from redlib.api.system import *
if is_py3():
	from urllib.parse import urlencode, urlparse, parse_qs
else:
	from urllib import urlencode
	from urlparse import urlparse, parse_qs

import json
from random import choice

from redlib.api.web import HtmlParser

from ..util import log
from ..service.image_context import ImageContext
from ..db import SearchTermList
from ..util.printer import printer
from .base import SourceError, SourceParams
from .base_source import BaseSource


class GoogleParams(SourceParams):
	name = 'google'


class Google(BaseSource):
	name 	= 'google'
	online	= True
	db	= False
	gen	= False

	search_base_url = "https://www.google.com/search?tbm=isch&"
	colors 		= ['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'purple', 'pink', 'white', 'gray', 'black', 'brown']
	user_agent 	= 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'

	def __init__(self):
		super(Google, self).__init__()


	def get_image(self, params=None):
		if self.image_urls_available():
			image_url = self.select_url()
			return image_url

		if params is None:
			params = GoogleParams()

		self.search(params)
		self.http_get_image_to_temp_file()

		return self._response


	def search(self, params):
		if params.query is None:
			params.query = SearchTermList().get_random()
			self.add_trace_step('random search term', params.query)

		if params.color is not None and not params.color in self.colors:
			log.error('%s is not a supported color for google image search. please choose from: %s'%(params.color, ', '.join(self.colors)))
			raise ServiceError()
		elif params.color is not None:
			self.add_trace_step('color', params.color)

		q_params = {
			'as_q'		: params.query,
			'as_st'		: 'y',
			'as_epq'	: '',
			'as_oq'		: '',
			'as_eq'		: '',
			'cr'		: '',
			'as_sitesearch' : '',
			'safe'		: 'active',
			'tbs'		: 'isz:lt,islt:xga' + ',ic:specific,isc:%s'%params.color if params.color is not None else ''
		}

		search_url = self.search_base_url + urlencode(q_params)

		self.add_trace_step('search', params.query)
		response = self.http_get(search_url, msg='searching google images', headers={'User-Agent': self.user_agent})

		self.extract_results(response)
		printer.printf('result', '%d images'%self.image_count, verbosity=2)
		
		
	def extract_results(self, response):
		etree = self.get_etree(response)
		result_div_path = './/div[@class=\'rg_di rg_el ivg-i\']'

		for div in etree.findall(result_div_path):
			a = div.find('.//a')
			if a is None:
				continue

			href = a.attrib.get('href', None)
			query = urlparse(href).query
			params = parse_qs(query)
			imgurl = params.get('imgurl', None)

			if imgurl is None:
				continue

			meta_div = div.find(".//div[@class='rg_meta']")
			image_context = None
			if meta_div is not None:
				meta = json.loads(meta_div.text)

				url 		= meta.get('isu', None)
				title		= meta.get('pt', None)
				description	= meta.get('s', None)

				if any([i != None for i in [url, title, description]]):
					image_context = ImageContext(url=url, title=title, description=description)

			self.add_url(imgurl[0], image_context)


	def get_etree(self, html):
		parser = HtmlParser()
		parser.feed(html)
		etree = parser.etree

		return etree

