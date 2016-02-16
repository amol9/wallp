
from redcmd.api import Subcommand, subcmd, Arg

from .list_mixin import ListMixin


class AddSubcommand(Subcommand, ListMixin):

	@subcmd
	def add(self, list_name=Arg(choices=ListMixin.list_choices, default=None), item=Arg(pos=True)):
		'''Add an item (url or name or string) to the given list.
		list_name: 	name of the list
		item: 		item to be added'''

		item_list = self.get_item_list(list_name)
		self.itemlist_call(item_list.add, item, True, commit=True)
		print('%s added to %s list'%(item, list_name))
		
