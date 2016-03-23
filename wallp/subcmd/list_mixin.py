
from redcmd.api import CommandError

from ..db import func as dbfunc
from ..db.exc import NotFoundError


class ListMixin:
	list_choices = [l.name for l in dbfunc.get_lists()]

	def get_item_list(self, list_name):
		item_list = [l for l in dbfunc.get_lists() if l.name == list_name]
		if len(item_list) == 0:
			raise CommandError('%s is not a valid list'%list_name)
		elif len(item_list) > 1:
			raise AppErrpr('too many lists named %s, something is very wrong'%list_name)
		return item_list[0]()


	def itemlist_call(self, func, *args, **kwargs):
		try:
			func(*args, **kwargs)
		except (ValueError, NotFoundError) as e:
			print(str(e))
			raise CommandError()

