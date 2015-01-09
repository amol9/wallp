from os.path import join as joinpath
import re
from urllib import urlencode
from random import randint

from service import Service, ServiceException
import web
from logger import log


search_url = "http://imgur.com/search?"
search_result_link_prefix = "http://imgur.com"
get_full_album = True


class Imgur(Service):
	name = 'imgur'

	def get_image(self, pictures_dir, basename, query=None):
		results = self.search(query)
		page_url = search_result_link_prefix + results[randint(0, len(results) - 1)]

		log.debug('selected url: ' + page_url)
		
		image_url = self.get_image_url_from_page(page_url)
		ext = image_url[image_url.rfind('.')+1:]
		try:
			save_path = joinpath(pictures_dir, basename, ext)
			web.download(image_url, save_path)
		except HTTPError:
			raise ServiceException

		return basename + '.' + ext


	def get_image_url_from_page(self, page_url):
		html = web.download(page_url)

		url_regex = re.compile(".*<div\s+id=\"content\".*?src=\"(.*?)\".*?</div>.*", re.M | re.S)
		matches = url_regex.findall(html)

		url = None
		if matches:
			print 'links on page'
			for m in matches:
				url = m
				print url

		log.debug('imgur url: ' + url)
		if not url.startswith('http'):
			url = 'http:' + url

		return url

	
	def search(self, query=None):
		if not query:
			qs = {
				'q': 'wallpapers'
			}
		else:
			qs = {
				'q_size_px': 'med',
				'q_size_mpx': 'med',
				'q_type': 'jpg',
				'q_all': query
			}

		url = search_url + urlencode(qs)
		#res = web.download(url)

		res = None
		with open('imgur.html', 'r') as f: res = f.read()

		link_regex = re.compile("<a.*?class=\"image-list-link\".*?href=\"(.*?)\"")
		matches = link_regex.findall(res)

		link_urls = []
		if matches:
			print 'found links'
			for m in matches:
				print m
				link_urls.append(m)

		return link_urls

'''
imgur mega dumps: 
http://imgur.com/gallery/wCBYO - 2163
http://imgur.com/gallery/hfHhb - 625
http://imgur.com/gallery/D3vya - 976
dump of dumps: http://imgur.com/a/GV71l?gallery - 52000
http://imgur.com/gallery/5vKwE
'''

if __name__ == '__main__':
	import sys
	i = Imgur()
	url = i.get_image_url_from_page(sys.argv[1])
	print url
	#i.search(sys.argv[1])

