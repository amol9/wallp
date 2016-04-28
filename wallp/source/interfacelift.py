import json
from random import choice
import re

from redlib.api.web import HtmlParser
from redlib.api.misc import Retry
from six.moves.urllib.parse import urlencode, urlparse, parse_qs
from asq.initiators import query

from ..util import log
from ..util.printer import printer
from .base import SourceError, SourceParams, Source
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from .image import Image
from ..desktop.desktop_factory import get_desktop
from ..db.app.config import Config


class InterfaceliftParams(SourceParams):
	name = 'interfacelift'

	def __init__(self, page=None):
		self.page = page
		self.hash_params = ['name']



class Interfacelift(Source):
	name 		= 'interfacelift'
	params_cls	= InterfaceliftParams
	online		= True
	db		= False
	gen		= False

	base_url = "https://interfacelift.com/wallpaper/downloads/date/any/index%d.html"
	root_url = "https://interfacelift.com"

	user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'


	def __init__(self):
		self._trace = Trace()
		self._http = HttpHelper()


	def get_image(self, params=None):
		if params is None:
			params = InterfaceliftParams()

		self._images = Images(params, cache=(params.page is None), cache_timeout='1d', trace=self._trace)

		if not self._images.available():
			url = self.parse(params)

		return self._http.download_image(self._images, self._trace, headers={'User-Agent': self.user_agent, 'Referer' : self.get_page_url()})


	def get_page_url(self):
		config = Config(group=self.name)
		page = config.pget('page', default=1)
		return self.base_url%page


	def parse(self, params):
		if params.page is not None:
			self.parse_page(params.page)
			return

		retry = Retry(retries=3, exp_bkf=False, delay=1, final_exc=SourceError('could not get unused images'))

		config = Config(group=self.name)
		page = config.pget('page', default=1)

		while retry.left():
			self.parse_page(page)

			if self._images.available():
				retry.cancel()
			else:
				page += 1
				config.pset('page', page)
				retry.retry()


	def parse_page(self, page):
		page_url = self.base_url%page

		html = self._http.get(page_url, msg='getting page', headers={'User-Agent': self.user_agent})
		etree = self.get_etree(html)

		scripts = etree.findall(".//script[@type='text/javascript']")
		script = next(iter(query(scripts).where(lambda s : (s.attrib.get('src') or '').find('inc_NEW') > -1)), None)

		js_url = self.root_url + script.attrib.get('src')
		js = self._http.get(js_url, msg='getting js', headers={'User-Agent': self.user_agent, 'Referer' : page_url})

		download_prefix_regex = re.compile("^.*getElementById.*?download_.*?innerHTML.*?<a\s+href=.*?/wallpaper/(.*?)/.*?>", re.M | re.S)
		match = download_prefix_regex.match(js)
		if match is None:
			raise SourceError()

		download_prefix = match.group(1)
		if download_prefix is None or download_prefix == '':
			raise SourceError('cannot form image urls')

		dt = get_desktop()
		dw, dh = dt.get_size()

		items = etree.findall(".//div[@class='item']")
		for item in items:
			a = item.findall(".//a")[0]
			img = item.findall(".//img")[0]

			src = img.attrib.get('src')
			filename = src.split('/')[-1]
			target_filename = re.sub(r'^(.*_)\d+x\d+(\..*)', r'\g<1>%dx%d\g<2>'%(dw, dh), filename)

			image = Image()
			image.url = self.root_url + '/wallpaper/' + download_prefix + '/' + target_filename

			image.title = img.attrib.get('alt')

			self._images.add(image)


	def get_etree(self, html):
		parser = HtmlParser()
		parser.feed(html)
		etree = parser.etree

		return etree


	def get_trace(self):
		return self._trace.steps

