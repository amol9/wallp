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

from .. import web
from ..util.logger import log
from .service import IHttpService
from ..db import SearchTermList, ImageTrace
from .image_mixin import ImageMixin


default_queries = ['flower', 'cheat sheet']
search_base_url = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&"


@implementer(IHttpService)
class Google(ImageMixin):
	name = 'google'

	def __init__(self):
		super(Google, self).__init__()


	def get_image_url(self, query=None, color=None):
		url = self.search(query)
		#ext = url[url.rfind('.')+1:]

		log.debug('selected url: %s'%url)
		#save_path = joinpath(pictures_dir, basename + '.' + ext)
		#download(url, save_path)

		return url


	def search(self, query=None):
		if query is None:
			query = SearchTermList().get_random() 

		params = {
			'q': query,
			'imgc': 'color', # or gray
			#'imgcolor'
			'rsz': 8,
			'imgsz': 'xxlarge' # xlarge, xxlarge, huge, large
		}

		url = search_base_url + urlencode(params) + "&start=" + str(0)
		try:
			res = web.func.get_page(url)
			jdata = json.loads(res)

			results = jdata['responseData']['results']

			urls = []
			for r in results:
				urls.append(r['url'])
			#print i['width'], 'x', i['height']
		except (HTTPError, ValueError):
			raise ServiceError()
		self._image_trace.append(ImageTrace(name='google search', data=query))

		image_url = choice(urls)
		self._image_trace.append(ImageTrace(name='select random url', data=image_url))
		return image_url

