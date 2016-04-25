
from redcmd.api import subcmd, CommandError

from .base import ConfigSubcommand
from ...db.app.imgur_album_list import ImgurAlbumList, ImgurAlbumListError
from ...db.app.query_list import QueryList, QueryListError
from ...db.app.subreddit_list import SubredditList, SubredditListError
from ...util.printer import printer


class ListSubcommand(ConfigSubcommand):

	@subcmd
	def list(self):
		'Manage lists.'
		pass


class ListOps:
	list_cls = None
	list_exc_cls = None

	def __init__(self):
		self._list = self.list_cls()


	def exc_call(self, method, *args, **kwargs):
		try:
			return method(*args, **kwargs)
		except self.list_exc_cls as e:
			print(e)
			raise CommandError()


	@subcmd
	def add(self, item):
		'''Add to list.
		item :	item to be added'''

		self.exc_call(self._list.add, item)
		print('%s added'%self.list_cls.item_name)

	@subcmd
	def remove(self, item):
		'''Remove from list.
		item :	item to be removed'''
		
		self.exc_call(self._list.remove, item)
		print('%s removed'%self.list_cls.item_name)


	@subcmd
	def enable(self, item):
		'''Enable an item.
		item :	item to be enabled'''

		self.exc_call(self._list.enable, item)
		print('%s enabled'%self.list_cls.item_name)

	@subcmd
	def disable(self, item):
		'''Disable an item.
		item :	item to be disabled'''
		
		self.exc_call(self._list.disable, item)
		print('%s disabled'%self.list_cls.item_name)


	@subcmd
	def dump(self):
		'Print entire list.'
		
		records = self.exc_call(self._list.get_all)
		for r in records:
			get = lambda col : getattr(r, col, None)
			state = 'enabled' if get('enabled') else 'disabled'
			printer.printf(get(self.list_cls.item_col), state)


class ImgurAlbumSubcommand(ListSubcommand):

	@subcmd
	def imgur_album(self):
		'Imgur album list.'
		pass


class ImgurAlbumListOps(ImgurAlbumSubcommand, ListOps):
	list_cls = ImgurAlbumList
	list_exc_cls = ImgurAlbumListError

	def __init__(self):
		ImgurAlbumSubcommand.__init__(self)
		ListOps.__init__(self)


class QuerySubcommand(ListSubcommand):

	@subcmd
	def query(self):
		'Query list.'
		pass


class QueryListOps(QuerySubcommand, ListOps):
	list_cls = QueryList
	list_exc_cls = QueryListError

	def __init__(self):
		QuerySubcommand.__init__(self)
		ListOps.__init__(self)


class SubredditSubcommand(ListSubcommand):

	@subcmd
	def subreddit(self):
		'Subreddit list.'
		pass


class SubredditListOps(SubredditSubcommand, ListOps):
	list_cls = SubredditList
	list_exc_cls = SubredditListError

	def __init__(self):
		SubredditSubcommand.__init__(self)
		ListOps.__init__(self)

