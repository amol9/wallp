
from redlib.api.misc import Singleton

from ..model.search_page_num import SearchPageNum
from .kvhelper import KVHelper


class SearchPageError(Exception):
	pass

class SearchPage(KVHelper):

	def __init__(self, group=None):
		KVHelper.__init__(self, SearchPageNum, SearchPageError, prefix=group)

