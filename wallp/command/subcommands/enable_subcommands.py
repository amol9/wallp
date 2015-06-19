
from ..subcommand import Subcommand, subcmd
from .list_mixin import ListMixin


class EnableSubcommands(Subcommand):
	service_choices = [s.name for s in service_factory.services]
	name_choices = Choices(ListMixin.list_choices + EnableSubcommands.service_choices, default=None)
	
	@subcmd
	def enable(self, name=name_choices, item=None):
		item_list = self.get_item_list()
		self.update(name, item, True)

		print('%s enabled in %s list'%(self._args.item, item_list.name))


	@subcmd
	def disable(self, name=name_choices, item=None):
		item_list = self.get_item_list()
		self.update(name, item, False)

		print('%s disabled in %s list'%(self._args.item, item_list.name))


	def update(self, name, item, state):
		if name in self.service_choices:
			config = Config()
			config.set(name + '.enabled', state)
		elif name in self.list_choices:
			if item is None:
				print('missing list item to be %s'%('enabled' if state else 'disabled'))

			if state == True:
				self.itemlist_call(item_list.enable, item)
			else:
				self.itemlist_call(item_list.disable, item)

