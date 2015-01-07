from os.path import join as joinpath
import re

from service import Service
import web
from wallp.logger import log


class Imgur(Service):
	name = 'imgur'

	def get_image(self, target_filepath):
		pass


	def get_image_url_from_page(self, page_url):
		html = web.download(page_url)

		url_regex = re.compile(".*<div\s+id=\"content\".*?src=\"(.*?)\".*?</div>.*", re.M | re.S)
		m = url_regex.match(html)

		url = None
		if m:
			url = m.group(1)

		log.debug('imgur url: ' + url)
		if not url.startswith('http'):
			url = 'http:' + url

		return url

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

