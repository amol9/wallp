import re
import json
from random import randint
from os.path import join as joinpath

from redlib.api.misc import Retry

from ..util.logger import log
from ..desktop import get_desktop, get_standard_desktop_size
from .base import SourceError, SourceParams, Source
from .image import Image
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from ..web.func import exists


class BingParams(SourceParams):
	name = 'bing'

	def __init__(self):
		self.hash_params = ['name']


class Bing(Source):
	name 		= 'bing'
	params_cls	= BingParams

	image_list_url 	= 'http://www.bing.com/gallery/home/browsedata'
	app_js_url 	= 'http://az615200.vo.msecnd.net/site/scripts/app.f21eb9ba.js'

	valid_sizes = [		#valid image sizes on bing
		(1366, 768),	#evaluated using test case TestBing::test_valid_image_sizes
		(1920, 1200)
	]
	
	def __init__(self):
		self._trace 	= Trace()
		self._http 	= HttpHelper()


	def get_image(self, params=None):
		params = BingParams()

		self._images = Images(params, cache=True, cache_timeout='1w', trace=self._trace)
		self._images.add_select_filter(lambda i : exists(i.url), retry=Retry(retries=10), msg='checking urls')

		if not self._images.available():
			self.get_image_urls()

		return self._http.download_image(self._images, self._trace)


	def get_nearest_size(self, width, height):
		nwidth = min(self.valid_sizes, key=lambda p: abs(width - p[0]))[0]
		nheight = min([(x, y) for (x, y) in self.valid_sizes if x == nwidth], key=lambda p: abs(height - p[1]))[1]

		return (nwidth, nheight)


	def get_image_urls(self):
		server_url = self.get_image_server()

		if server_url == None:
			log.error('bing: no valid image server found in %s'%self.app_js_url)
			raise SourceError()

		ext = 'jpg'
		width, height = get_desktop().get_size()
		width, height = get_standard_desktop_size(width, height)

		if not (width, height) in self.valid_sizes:
			width, height = self.get_nearest_size(width, height)

		jsfile = self._http.get(self.image_list_url, msg='getting image list')

		data_regex = re.compile(".*browseData=({.*});.*")
		m = data_regex.match(jsfile)

		if m:
			data = m.group(1)
			jdata = json.loads(data)

			for i in range(len(jdata['imageNames'])):
				image = Image()

				image_name = jdata['imageNames'][i]
				image.url = 'http:' + server_url + image_name + '_' + str(width) + 'x' + str(height) + '.' + ext

				desc_items = ['countries', 'tags', 'holidays', 'regions', 'colors', 'categories']
				image.description = '\n'.join(['{0:<10} : {1}'.format(item, jdata[item][i].rstrip(',')) for item in desc_items])

				self._images.add(image)
		
		return None


	def get_image_server(self):
		js = self._http.get(self.app_js_url, msg='getting server list')

		server_url_regex = re.compile(".*(\/\/.*?\.vo\.msecnd\.net\/files\/).*", re.M | re.S)
		m = server_url_regex.match(js)

		if m:
			url = m.group(1)
			return url
		return None


	def get_trace(self):
		return self._trace.steps

