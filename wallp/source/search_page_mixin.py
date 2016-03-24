
from ..db import SearchPage, SearchPageError


class SearchPageMixin(object):

	def __init__(self):
		self._prefix = self.name + '.'
		self._search_page = SearchPage()


	def search_page_get(self, name, default=0):
		try:
			return self._search_page.get(self._prefix + name)
		except SearchPageError:
			self.search_page_add(name, default)
			return default


	def search_page_set(self, name, value):
		try:
			self._search_page.set(self._prefix + name, value)
		except SearchPageError:
			self.search_page_add(name, value)	

	def search_page_add(self, name, value):
		self._search_page.add(self._prefix + name, value, type(value))
		self._search_page.commit()

