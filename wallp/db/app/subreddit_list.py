
from .itemlist import ItemList
from ..model.subreddit import Subreddit


class SubredditListError(Exception):
	pass


class SubredditList(ItemList):
	item_name	= 'subreddit'
	table		= Subreddit
	item_col	= 'name'
	exc_cls		= SubredditListError

