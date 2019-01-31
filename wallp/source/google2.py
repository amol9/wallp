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
from .filters.fansshare import FansshareFilter


class Google2Params(SourceParams):
	name = 'google2'

        def __init__(self, query=None):
		self.query	= query

		self.hash_params = ['query']


class Google2(Source):
	name 		= 'google2'
	params_cls 	= Google2Params
	online		= True
	db		= False
	gen		= False

	def __init__(self):
		#super(Google, self).__init__()
		pass


	def get_image(self, params=None):
		if params is None:
			params = Google2Params()

		self._trace = Trace()
		self._images = Images(params, cache=True, cache_timeout='1d', trace=self._trace)

		fansshare_filter = FansshareFilter(referer=self.host_url)
		self._images.add_select_filter(fansshare_filter.filter)

		self._http = HttpHelper()

		if not self._images.available():
			self.search(params)

		return self._http.download_image(self._images, self._trace, headers={'User-Agent': self.user_agent, 'Referer': self.host_url})


	def search(self, params):
		if params.query is None:
			params.query = QueryList().random()
			self._trace.add_step('random search term', params.query)

		self._trace.add_step('search', params.query)

                gid = gw.GoogleImagesDownloader()
                urls = gid.get_urls(params.query, related=False)

		self.extract_results(response)
		printer.printf('result', '%d images'%self._images.count, verbosity=2)
		
		
	def add_urls(self, urls):
            for url in urls:
                image = Image()
                image.url 	= meta.get('ou', None)
                self._images.add(image)




	def get_trace(self):
		return self._trace.steps

