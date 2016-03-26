import json
from random import choice
import re

from redlib.api.web import HtmlParser
from six.moves.urllib.parse import urlencode, urlparse, parse_qs
from asq.initiators import query

from ..util import log
from ..util.printer import printer
from .base import SourceError, SourceParams, Source
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from .images import Image


class InterfaceliftParams(SourceParams):
	name = 'interfacelift'

	def __init__(self, page=None):
		self.page = page
		self.hash_params = ['name']



class Interfacelift(Source):
	name 	= 'interfacelift'
	online	= True
	db	= False
	gen	= False

	base_url = "https://interfacelift.com/wallpaper/downloads/date/any/index%d.html"
	js_base_url = "https://interfacelift.com"

	user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'


	def __init__(self):
		pass


	def get_image(self, params=None):
		if params is None:
			params = InterfaceliftParams()


		self._http = HttpHelper()
		self._images = Images(params, cache=False)

		self._trace = Trace()

		if not self._images.available():
			url = self.parse()

		return self._http.download_image(self._images, self._trace, headers={'User-Agent': self.user_agent, 'Referer' : url})


	def parse(self):
		page = 1
		url = self.base_url%page

		html = self._http.get(url, msg='getting page', headers={'User-Agent': self.user_agent})
		etree = self.get_etree(html)

		scripts = etree.findall(".//script[@type='text/javascript']")
		script = next(iter(query(scripts).where(lambda s : (s.attrib.get('src') or '').find('inc_NEW') > -1)), None)

		js_url = self.js_base_url + script.attrib.get('src')
		js = self._http.get(js_url, msg='getting js', headers={'User-Agent': self.user_agent, 'Referer' : url})

		download_prefix_regex = re.compile("^.*getElementById.*?download_.*?innerHTML.*?<a\s+href=.*?/wallpaper/(.*?)/.*?>", re.M | re.S)
		match = download_prefix_regex.match(js)
		if match is None:
			raise SourceError()

		download_prefix = match.group(1)

		items = etree.findall(".//div[@class='item']")
		for item in items:
			a = item.findall(".//a")[0]
			img = item.findall(".//img")[0]

			image = Image()
			
			src = img.attrib.get('src')
			filename = src.split('/')[-1]
			dres = '1366x768'

			#import pdb; pdb.set_trace()
			target_filename = re.sub(r'^(.*_)\d+x\d+(\..*)', r'\g<1>%s\g<2>'%dres, filename)

			image.url = self.js_base_url + '/wallpaper/' + download_prefix + '/' + target_filename
			#print image.url

			image.title = img.attrib.get('alt')

			self._images.add(image)

		return url


	def get_etree(self, html):
		parser = HtmlParser()
		parser.feed(html)
		etree = parser.etree

		return etree


	def get_trace(self):
		return self._trace.steps

