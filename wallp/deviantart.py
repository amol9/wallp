from mangoutils.system import *
if is_py3():
	from urllib.parse import urlencode
else:
	from urllib import urlencode

from random import choice
import xml.etree.ElementTree as ET
from os.path import join as joinpath

import wallp.web as web
from wallp.logger import log
from wallp.config import config
from wallp.desktop_factory import get_desktop
from wallp.service import Service, service_factory, ServiceException


rss_url_base = 'http://backend.deviantart.com/rss.xml?type=deviation&order=11&boost:popular&'
xmlns = {'media': 'http://search.yahoo.com/mrss/'}
search_terms = ['tower', 'anime', 'art', 'flower', 'movie', 'nature', 'space', 'lego']


class DeviantArt(Service):
	name = 'deviantart'

	def get_image(self, pictures_dir, basename, query=None, color=None):
		if query is None:
			slist = config.get_list('deviantart', 'search_terms', default=search_terms)
			query = choice(slist)
	
		params = {}
		params['q'] = query

		width, height = get_desktop().get_size()		
		params['q'] += ' width:' + str(width) + ' height:' + str(height)

		url = rss_url_base + urlencode(params)
		log.info('da rss url: ' + url)

		res = None 
		with web.download(url, eh=True) as d:
			res = d.start()
	
		rss = ET.fromstring(res)

		image_urls = []
		for item in rss.findall('./channel/item', xmlns):
			mr = item.findall('media:rating', xmlns)[0]
			if mr.text == 'nonadult':
				mc = item.findall('media:content', xmlns)
				if len(mc) == 0:
					continue
				mc = mc[0]

				image_width = int(mc.get('width')) if mc.get('width') != None else 0
				image_height = int(mc.get('height')) if mc.get('height') != None else 0
				#debug_p('da url: ' + mc.get('url') + '  ' + str(image_width) + 'x' + str(image_height))
				
				if (image_width >= width * 0.9) and (image_height >= height * 0.9):
					image_urls.append(mc.get('url'))

		download_url = choice(image_urls)
		log.info('da selected url: ' + download_url)

		ext = download_url[download_url.rfind('.')+1:]
		save_filepath = joinpath(pictures_dir, basename) + '.' + ext

		with web.download(download_url, save_filepath, eh=True) as d:
			d.start()

		return basename + '.' + ext


if config.get(DeviantArt.name, 'enabled', default=True, type=bool):
	service_factory.add(DeviantArt.name, DeviantArt)
