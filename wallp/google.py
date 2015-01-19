import json
from urllib import urlencode
from os.path import join as joinpath
from random import randint

from wallp.service import Service, service_factory
import wallp.web as web


queries = ['parrot', 'wallpaper', 'flower', 'cheat sheet']
search_base_url = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&"

class Google(Service):
	name = 'google'

	def get_image(self, pictures_dir, basename, query=None):
		query = query if query else queries[randint(0, len(queries))]
		params = {
			'q': query,
			'imgc': 'color', # or gray
			#'imgcolor'
			'rsz': 8,
			'imgsz': 'large' # xlarge, xxlarge, huge
		}

		url = search_base_url + urlencode(params) + "&start=" + str(0)
		res = web.download(url)
		jdata = json.load(res)

		results = j['responseData']['results']
			
		#print i['url']
		#print i['width'], 'x', i['height']


service_factory.add(Google.name, Google)

