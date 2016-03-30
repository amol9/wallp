
from redlib.api.web import HtmlParser

from .base import SourceError


class HtmlHelper:

	def get_etree(self, html):
		parser = HtmlParser()
		parser.feed(html)
		etree = parser.etree

		return etree

	def parse_error(self, msg):
		raise SourceError('parse error: %s'%msg)

