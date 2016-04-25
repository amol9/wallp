
from .itemlist import ItemList
from ..model.search_term import SearchTerm


class QueryListError(Exception):
	pass


class QueryList(ItemList):
	item_name	= 'query'
	table		= SearchTerm
	item_col	= 'term'
	exc_cls		= QueryListError

