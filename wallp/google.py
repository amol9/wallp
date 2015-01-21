import json
from urllib import urlencode
from os.path import join as joinpath
from random import choice

from wallp.service import Service, service_factory
import wallp.web as web
from wallp.config import config
from wallp.logger import log


default_queries = ['parrot', 'wallpaper', 'flower', 'cheat sheet']
search_base_url = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&"

class Google(Service):
	name = 'google'

	def get_image(self, pictures_dir, basename, query=None):
		url = self.get_image_url(query)
		ext = url[url.rfind('.')+1:]

		log.debug('selected url: %s'%url)
		save_path = joinpath(pictures_dir, basename + '.' + ext)
		with web.download(url, save_path, eh=True) as d:
			d.start()
		#web.download(url, save_path)

		return basename + '.' + ext 


	def get_image_url(self, query=None):
		if query is None:
			queries = config.get(Google.name, 'queries', default=default_queries)
			query = choice(queries)

		params = {
			'q': query,
			'imgc': 'color', # or gray
			#'imgcolor'
			'rsz': 8,
			'imgsz': 'xxlarge' # xlarge, xxlarge, huge, large
		}

		url = search_base_url + urlencode(params) + "&start=" + str(0)
		try:
			res = web.download(url)
			jdata = json.loads(res)

			results = jdata['responseData']['results']

			urls = []
			for r in results:
				urls.append(r['url'])
			#print i['width'], 'x', i['height']
		except HTTPError, ValueError:
			raise ServiceException()
			
		return choice(urls)

if config.get(Google.name, 'enabled', default=True, type=bool):
	service_factory.add(Google.name, Google)


