
from .itemlist import ItemList
from ..model.query import Query


class QueryListError(Exception):
	pass


class QueryList(ItemList):
	item_name	= 'query'
	table		= Query
	item_col	= 'term'
	exc_cls		= QueryListError

