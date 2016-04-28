import json

from redlib.api.web import HtmlParser
from six.moves.urllib.parse import urlencode, urlparse, parse_qs

from ..util import log
from ..db.app.query_list import QueryList
from ..util.printer import printer
from .base import SourceError, SourceParams, Source
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from .image import Image


class GoogleParams(SourceParams):
	name = 'google'

	def __init__(self, query=None, color=None, safesearch=True):
		self.query	= query
		self.color	= color
		self.safesearch	= safesearch

		self.hash_params = ['query', 'color', 'safesearch']


class Google(Source):
	name 		= 'google'
	params_cls 	= GoogleParams
	online		= True
	db		= False
	gen		= False

	search_base_url = "https://www.google.com/search?tbm=isch&"
	colors 		= ['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'purple', 'pink', 'white', 'gray', 'black', 'brown']
	user_agent 	= 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'


	def __init__(self):
		#super(Google, self).__init__()
		pass


	def get_image(self, params=None):
		if params is None:
			params = GoogleParams()

		self._trace = Trace()
		self._images = Images(params, cache=True, cache_timeout='1d', trace=self._trace)

		self._http = HttpHelper()

		if not self._images.available():
			self.search(params)

		return self._http.download_image(self._images, self._trace)


	def search(self, params):
		if params.query is None:
			params.query = QueryList().random()
			self._trace.add_step('random search term', params.query)

		if params.color is not None and not params.color in self.colors:
			msg = '%s is not a supported color for google image search. please choose from: %s'%(params.color, ', '.join(self.colors))
			log.error(msg)
			raise SourceError(msg)

		elif params.color is not None:
			self._trace.add_step('color', params.color)

		q_params = {
			'as_q'		: params.query,
			'as_st'		: 'y',
			'as_epq'	: '',
			'as_oq'		: '',
			'as_eq'		: '',
			'cr'		: '',
			'as_sitesearch' : '',
			'safe'		: 'active' if params.safesearch else 'images',
			'tbs'		: 'isz:lt,islt:xga' + ',ic:specific,isc:%s'%params.color if params.color is not None else ''
		}

		search_url = self.search_base_url + urlencode(q_params)

		self._trace.add_step('search', params.query)
		response = self._http.get(search_url, msg='searching google images', headers={'User-Agent': self.user_agent})

		self.extract_results(response)
		printer.printf('result', '%d images'%self._images.count, verbosity=2)
		
		
	def extract_results(self, response):
		etree = self.get_etree(response)
		result_div_path = './/div[@class=\'rg_di rg_el ivg-i\']'

		for div in etree.findall(result_div_path):
			meta_div = div.find(".//div[@class='rg_meta']")

			if meta_div is not None:
				meta = json.loads(meta_div.text)

				image = Image()

				image.url 	= meta.get('ou', None)
				image.width 	= meta.get('ow', None)
				image.height 	= meta.get('oh', None)

				image.context_url 	= meta.get('ru', None)
				image.title		= meta.get('pt', None)
				image.description	= meta.get('s', None)
				image.ext		= meta.get('ity', None)

				self._images.add(image)


	def get_etree(self, html):
		parser = HtmlParser()
		parser.feed(html)
		etree = parser.etree

		return etree


	def get_trace(self):
		return self._trace.steps

