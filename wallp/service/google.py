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
from ..db import SearchTermList


@implementer(IHttpService)
class Google(ImageInfoMixin):
	name = 'google'
	search_base_url = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&"

	def __init__(self):
		super(Google, self).__init__()


	def get_image_url(self, query=None, color=None):
		image_urls = self.search(query, color)

		image_url = choice(image_urls)
		self.add_trace_step('selected random url', image_url)
		log.debug('selected url: %s'%image_url)

		return image_url


	def search(self, query, color):
		if query is None:
			query = SearchTermList().get_random()

		if color is None:
			color = choice(list(colors.keys()))
		self.add_trace_step('preferred color', color)

		params = {
			'q': 		query,
			'imgc': 	'color', 	# or gray
			'imgcolor': 	color,
			'rsz': 		8,
			'imgsz': 	'xxlarge' 	# or xlarge, xxlarge, huge, large
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
			image_urls.append(r['url'])


		return image_urls

