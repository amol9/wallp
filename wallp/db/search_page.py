
from . import SearchPageNum
from .namevalueset import NameValueSet, NameError

from redlib.api.misc import Singleton

from .nv_shortcut_mixin import NVShortcutMixin


class SearchPageError(NameError):
	nv_typename = 'search_page_num'


class _SearchPage(NVShortcutMixin, NameValueSet):
	nvtype = SearchPageNum
	name_err_type = SearchPageError

	def __init__(self):
		super(_SearchPage, self).__init__()


class SearchPage(Singleton):
	classtype = _SearchPage

