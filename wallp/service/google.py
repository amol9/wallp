from mutils.system import *
if is_py3():
	from urllib.parse import urlencode
	from urllib.error import HTTPError
else:
	from urllib import urlencode
	from urllib2 import HTTPError

import json
from random import choice
from os.path import join as joinpath
from zope.interface import implementer

from mutils.misc.colors import colors

from .. import web
from ..util import log
from .service import IHttpService
from .image_info_mixin import ImageInfoMixin
from .image_urls_mixin import ImageUrlsMixin
from .image_context import ImageContext
from ..db import SearchTermList


@implementer(IHttpService)
class Google(ImageInfoMixin, ImageUrlsMixin):
	name = 'google'
	search_base_url = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&"

	def __init__(self):
		super(Google, self).__init__()


	def get_image_url(self, query=None, color=None):
		if self.image_urls_available():
			image_url = self.select_url()
			return image_url

		self.search(query, color)
		image_url = self.select_url()

		return image_url


	def search(self, query, color):
		if query is None:
			query = SearchTermList().get_random()
			self.add_trace_step('random search term', query)

		if color is None:
			color = choice(list(colors.keys()))
			self.add_trace_step('random color', color)
		else:
			self.add_trace_step('color', color)

		params = {
			'q'		: query,
			'imgc'		: 'color', 	# or gray
			'imgcolor'	: color,
			'rsz'		: 8,
			'imgsz'		: 'xxlarge' 	# or xlarge, xxlarge, huge, large
		}

		search_url = self.search_base_url + urlencode(params) + "&start=" + str(0)
		response = web.func.get_page(search_url)
		self.add_trace_step('searched google', query)

		jdata = json.loads(response)
		results = None

		try:
			results = jdata['responseData']['results']
		except (ValueError):
			raise ServiceError()

		image_urls = []
		for r in results:
			self.add_url(r['url'], ImageContext(title=r['titleNoFormatting'], url=r['originalContextUrl']))
		

