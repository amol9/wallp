
from redlib.api.net import AbsUrl
from redlib.api.web import HtmlParser

from ..http_helper import HttpHelper


class FansshareFilter:
	domain = 'fansshare.com'
	user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'
	
	def __init__(self, referer=None):
		self._referer = referer


	def filter(self, image):
		image_url = AbsUrl(image.url)
		domain = image_url.get_domain()
		subdomain = image_url.get_subdomain()

		if domain != self.domain or subdomain.startswith('cdn'):
			return True

		http = HttpHelper()
		response = http.get(image.context_url, msg='getting fansshare page', headers={'User-Agent': self.user_agent, 'Referer': self._referer})

		url = self.get_image_url(response)
		if url is not None and len(url) > 10:
			image.url = url

		return True


	def get_image_url(self, html):
		etree = self.get_etree(html)

		div_mainarea = etree.find(".//div[@id=\'mainarea\']")
		a = div_mainarea.find(".//a")
		url = a.attrib['href']

		return url


	def get_etree(self, html):
		parser = HtmlParser()
		parser.feed(html)
		etree = parser.etree

		return etree
	
