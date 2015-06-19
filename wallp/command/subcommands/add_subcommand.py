
from ..subcommand import Subcommand, subcmd, Choices, PositionalArg
from .list_mixin import ListMixin


class AddSubcommand(Subcommand, ListMixin):
	list_name_choices = Choices(ListMixin.list_choices, default=None)

	@subcmd
	def add(self, list_name=list_name_choices, item=PositionalArg()):
		item_list = self.get_item_list(list_name)
		self.itemlist_call(item_list.add, item, True, commit=True)
		print('%s added to %s list'%(item, list_name))
		
