import re
import json
from random import randint
from os.path import join as joinpath
from zope.interface import implementer

from redlib.api.misc import Retry

from ..web.func import get, exists, HttpError
from ..util.logger import log
from ..desktop import get_desktop, get_standard_desktop_size
from .image_context import ImageContext
from .base import SourceError, SourceParams
from .base_source import BaseSource


class BingParams(SourceParams):
	name = 'bing'

	def __init__(self):
		pass


class Bing(BaseSource):
	name 		= 'bing'

	image_list_url 	= 'http://www.bing.com/gallery/home/browsedata'
	app_js_url 	= 'http://az615200.vo.msecnd.net/site/scripts/app.f21eb9ba.js'

	valid_sizes = [		#valid image sizes on bing
		(1366, 768),	#evaluated using test case TestBing::test_valid_image_sizes
		(1920, 1200)
	]
	
	def __init__(self):
		super(Bing, self).__init__()
		self._check_if_url_exists = True


	def get_image(self, params=None):
		self.get_image_urls()

		if self.image_count == 0:
			raise SourceError('no images found at %s'%self.image_list_url)
		
		return self.http_get_image_to_temp_file()


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

		jsfile = self.http_get(self.image_list_url, msg='getting image list')

		data_regex = re.compile(".*browseData=({.*});.*")
		m = data_regex.match(jsfile)

		if m:
			data = m.group(1)
			jdata = json.loads(data)

			for i in range(len(jdata['imageNames'])):
				image_name = jdata['imageNames'][i]
				image_url = 'http:' + server_url + image_name + '_' + str(width) + 'x' + str(height) + '.' + ext

				desc = 'country    : %s\ntags       : %s\nholidays   : %s\
					\nregion     : %s\ncolor      : %s\ncategories : %s'\
					%(jdata['countries'][i], jdata['tags'][i], jdata['holidays'][i],
					jdata['regions'][i], jdata['colors'][i], jdata['categories'][i])

				self.add_url(image_url, ImageContext(description=desc))
		
		return None


	def get_image_server(self):
		js = self.http_get(self.app_js_url, msg='getting server list')

		server_url_regex = re.compile(".*(\/\/.*?\.vo\.msecnd\.net\/files\/).*", re.M | re.S)
		m = server_url_regex.match(js)

		if m:
			url = m.group(1)
			return url
		return None

