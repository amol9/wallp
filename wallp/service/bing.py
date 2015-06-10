from mutils.system import *
if is_py3():
	from urllib.error import HTTPError
else:
	from urllib2 import HTTPError

import re
import json
from random import randint
from os.path import join as joinpath
from zope.interface import implementer

from .. import web
from ..util.logger import log
from . import IHttpService, ServiceError
from ..desktop import get_desktop, get_standard_desktop_size
from ..util import Retry
from .image_mixin import ImageMixin


@implementer(IHttpService)
class Bing(ImageMixin):
	name 		= 'bing'
	image_list_url 	= 'http://www.bing.com/gallery/home/browsedata'
	app_js_url 	= 'http://az615200.vo.msecnd.net/site/scripts/app.f21eb9ba.js'

	valid_sizes = [		#valid image sizes on bing
		(1366, 768),	#evaluated using test case TestBing::test_valid_image_sizes
		(1920, 1200)
	]
	
	def __init__(self):
		super(Bing, self).__init__()


	def get_image_url(self, query=None, color=None):
		image_names = self.get_image_names()

		if image_names is None or len(image_names) == 0:
			log.error('bing: no images found at %s'%image_list_url)
			raise ServiceError()

		server_url = self.get_image_server()

		if server_url == None:
			log.error('bing: no valid image server found in %s'%self.app_js_url)
			raise ServiceError()

		ext = 'jpg'
		width, height = get_desktop().get_size()
		width, height = get_standard_desktop_size(width, height)

		if not (width, height) in self.valid_sizes:
			width, height = self.get_nearest_size(width, height)

		retry = Retry(retries=3, final_exc=ServiceError())

		while (retry.left()):		
			image_name = image_names[randint(0, len(image_names) - 1)]
			image_url = 'http:' + server_url + image_name + '_' + str(width) + 'x' + str(height) + '.' + ext
			log.debug('bing image url: ' + image_url)

			#save_filepath = joinpath(pictures_dir, basename) + '.' + ext

			if web.func.exists(image_url):
				return image_url
			retry.retry()

		return image_url


	def get_nearest_size(self, width, height):
		nwidth = min(self.valid_sizes, key=lambda p: abs(width - p[0]))[0]
		nheight = min([(x, y) for (x, y) in self.valid_sizes if x == nwidth], key=lambda p: abs(height - p[1]))[1]

		return (nwidth, nheight)


	def get_image_names(self):
		jsfile = web.func.get_page(self.image_list_url) 

		data_regex = re.compile(".*browseData=({.*});.*")
		m = data_regex.match(jsfile)

		if m:
			data = m.group(1)
			jdata = json.loads(data)
			return jdata['imageNames']
		
		return None


	def get_image_server(self):
		js = web.func.get_page(self.app_js_url)

		server_url_regex = re.compile(".*(\/\/.*?\.vo\.msecnd\.net\/files\/).*", re.M | re.S)
		m = server_url_regex.match(js)

		if m:
			url = m.group(1)
			return url
		return None

