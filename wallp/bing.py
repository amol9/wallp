from mutils.system import *
if is_py3():
	from urllib.error import HTTPError
else:
	from urllib2 import HTTPError

import re
import json
from random import randint
from os.path import join as joinpath

import wallp.web as web
from wallp.logger import log
from wallp.config import config
from wallp.desktop_factory import get_desktop
from wallp.service import Service, service_factory, ServiceException
from wallp.standard_desktop_sizes import get_standard_desktop_size


image_list_url = 'http://www.bing.com/gallery/home/browsedata'
app_js_url = 'http://az615200.vo.msecnd.net/site/scripts/app.f21eb9ba.js'


class Bing(Service):
	name = 'bing'
	valid_sizes = [		#valid image sizes on bing
		(1366, 768),	#evaluated using test case TestBing::test_valid_image_sizes
		(1920, 1200)
	]
		

	def get_image(self, pictures_dir, basename, query=None, color=None):
		image_names = self.get_image_names()

		if image_names is None or len(image_names) == 0:
			log.error('bing: no images found at %s'%image_list_url)
			raise ServiceException()

		server_url = self.get_image_server()

		if server_url == None:
			log.error('bing: no valid image server found in %s'%app_js_url)
			raise ServiceException()

		ext = 'jpg'
		width, height = get_desktop().get_size()
		width, height = get_standard_desktop_size(width, height)

		if not (width, height) in self.valid_sizes:
			width, height = self.get_nearest_size(width, height)

		try_image = 3

		while (try_image):		
			image_name = image_names[randint(0, len(image_names) - 1)]
			image_url = 'http:' + server_url + image_name + '_' + str(width) + 'x' + str(height) + '.' + ext
			log.debug('bing image url: ' + image_url)

			save_filepath = joinpath(pictures_dir, basename) + '.' + ext
			try:
				web.download(image_url, save_filepath)
				try_image = 0
			except HTTPError as e:
				if e.code == 404:
					if try_image == 0:
						raise ServiceException()
					try_image -= 1
				else:
					try_image = 0
					raise ServiceException()

		return basename + '.' + ext


	def get_nearest_size(self, width, height):
		nwidth = min(self.valid_sizes, key=lambda p: abs(width - p[0]))[0]
		nheight = min([(x, y) for (x, y) in self.valid_sizes if x == nwidth], key=lambda p: abs(height - p[1]))[1]

		return (nwidth, nheight)


	def get_image_names(self):
		res = None
		with web.download(image_list_url, eh=True) as d:
			res = d.start()
		jsfile = res

		data_regex = re.compile(".*browseData=({.*});.*")
		m = data_regex.match(jsfile)

		if m:
			data = m.group(1)
			jdata = json.loads(data)
			return jdata['imageNames']
		
		return None


	def get_image_server(self):
		res = None
		with web.download(app_js_url, eh=True) as d:
			res = d.start()
		js = res

		server_url_regex = re.compile(".*(\/\/.*?\.vo\.msecnd\.net\/files\/).*", re.M | re.S)
		m = server_url_regex.match(js)

		if m:
			url = m.group(1)
			return url
		return None


if config.get(Bing.name, 'enabled', default=True, type=bool):
	service_factory.add(Bing.name, Bing)

