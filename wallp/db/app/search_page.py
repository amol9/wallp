
from redlib.api.misc import Singleton

from ..search_page_num import SearchPageNum
from ..namevalueset import NameValueSet, NameError
from ..nv_shortcut_mixin import NVShortcutMixin
from .nvhelper import NVHelper


class SearchPageError(NameError):
	nv_typename = 'search_page_num'


class SearchPage(NVShortcutMixin, NameValueSet, NVHelper):
	nvtype = SearchPageNum
	name_err_type = SearchPageError

	def __init__(self, group=None):
		super(SearchPage, self).__init__()
		NVHelper.__init__(self, group=group)

