import json
import re
from os.path import join as joinpath
from random import randint
from urllib2 import HTTPError

from wallp.service import Service, service_factory, ServiceException
import wallp.web as web
from wallp.desktop import get_desktop
from wallp.logger import log


image_list_url = 'http://www.bing.com/gallery/home/browsedata'
app_js_url = 'http://az615200.vo.msecnd.net/site/scripts/app.f21eb9ba.js'


class Bing(Service):
	name = 'bing'

	def get_image(self, pictures_dir, basename, choice=None):
		res = None
		with web.download(image_list_url, eh=True) as d:
			res = d.start()
		jsfile = res

		data_regex = re.compile(".*browseData=({.*});.*")
		m = data_regex.match(jsfile)

		image_names = []
		if m:
			data = m.group(1)
			jdata = json.loads(data)
			image_names = jdata['imageNames']

		server_url = self.get_bing_image_server()
		if server_url == None:
			log.error('no valid bing image server found')
			return

		ext = 'jpg'
		width, height = get_desktop().get_size()
		try_image = True

		while (try_image):		
			image_name = image_names[randint(0, len(image_names) - 1)]
			image_url = 'http:' + server_url + image_name + '_' + str(width) + 'x' + str(height) + '.' + ext
			log.debug('bing image url: ' + image_url)

			save_filepath = joinpath(pictures_dir, basename) + '.' + ext
			try:
				web.download(image_url, save_filepath)
				try_image = False
			except HTTPError as e:
				if e.code == 404:
					try_image = True
				else:
					try_image = False
					raise ServiceException()
				

		return basename + '.' + ext


	def get_bing_image_server(self):
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


service_factory.add(Bing.name, Bing)
