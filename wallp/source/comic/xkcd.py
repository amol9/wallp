from datetime import datetime
import json

from redlib.api.web import HtmlParser
from redlib.api.net import AbsUrl, RelUrl
from asq.initiators import query

from ...util.printer import printer
from ..base import SourceError, SourceParams, Source
from ..images import Images
from ..http_helper import HttpHelper
from ..html_helper import HtmlHelper
from ..trace import Trace
from ..image import Image


class XkcdParams(SourceParams):
	name = 'xkcd'

	def __init__(self, latest=False, query=None, year=None):
		self.query	= query
		self.year	= year
		self.latest	= latest

		self.hash_params = ['name']


class Xkcd(Source):
	name = 'xkcd'
	params_cls = XkcdParams

	archive_url 	= 'http://xkcd.com/archive'
	base_url 	= 'http://xkcd.com'
	json_suffix 	= 'info.0.json'
	author		= 'Randall Munroe'


	def __init__(self):
		self._trace = Trace()
		self._http = HttpHelper()


	def get_image(self, params):
		self._params = params or XkcdParams()

		def select_latest():
			return self.get_latest()

		custom_select = select_latest if self._params.latest else None

		self._images = Images(self._params, cache=True, cache_timeout='1w', image_alias='comic', custom_select=custom_select, trace=self._trace)

		self._images.add_db_filter(lambda i, d : i.context_url is None or not d.seen_by_context_url(i.context_url))
		self._images.add_list_filter(lambda i, l : i.context_url is None or 
				len(query(l).where(lambda li : li.context_url == i.context_url).to_list()) == 0)

		if not self._params.latest:
			self._images.add_select_filter(self.get_comic_image_url)

		if not self._images.available():
			self.scrape()

		return self._http.download_image(self._images, self._trace)


	def scrape(self):
		html_text = self._http.get(self.archive_url, msg='getting archive')

		html = HtmlHelper()
		etree = html.get_etree(html_text)

		links = etree.findall(".//div[@id='middleContainer']//a")

		cb = printer.printf('comics', '?', col_updt=True)
		c = 0
		for link in links:
			image = Image()

			image.context_url = self.base_url + (link.attrib.get('href') or html.parse_error('link href'))
			image.title = link.text
			image.user = self.author

			date = link.attrib.get('title') or html.parse_error('link title')
			image.date = self.parse_date(date)
			image.title += image.date.strftime(' (%d %b %Y)')

			self._images.add(image)

			c += 1
			cb.col_updt_cb(2, str(c))
		cb.col_updt_cp()


	def parse_date(self, date_str):
		try:
			date = datetime.strptime(date_str, '%Y-%m-%d')
			return date
		except ValueError as e:
			html.parse_error(str(e))


	def get_comic_image_url(self, image):
		json_text = self._http.get(image.context_url + self.json_suffix, msg='getting comic info')
		info = json.loads(json_text)

		image.url = info.get('img') 
		image.description = info.get('alt')

		return image


	def get_latest(self):
		json_text = self._http.get(self.base_url + '/' + self.json_suffix, msg='getting comic info')
		info = json.loads(json_text)

		self._trace.add_step('latest comic', self.base_url + '/' + str(info.get('num')))
		image = Image()

		image.url 	= info.get('img')
		image.date 	= self.parse_date('%s-%s-%s'%(info.get('year'), info.get('month'), info.get('day')))
		image.title	= info.get('title') + image.date.strftime(' (%d %b %Y)')
		image.user	= self.author

		image.description = info.get('alt')

		return image


	def get_trace(self):
		return self._trace.steps

