
from ..subcommand import Subcommand, subcmd, Choices, PositionalArg
from .list_mixin import ListMixin
from ...service import ServiceFactory
from ..exc import CommandError
from ...db import Config


class EnableSubcommands(Subcommand, ListMixin):
	service_choices = [n for n, _ in ServiceFactory().services]
	name_choices = Choices(ListMixin.list_choices + service_choices, default=None)
	
	@subcmd
	def enable(self, name=name_choices, item=PositionalArg(nargs='?')):
		'''help: enable a service or an item in a list.
		name: name of the service or value of an item in a list
		item: item to be enabled, (not needed if name is a service)'''

		self.update(name, item, True)


	@subcmd
	def disable(self, name=name_choices, item=PositionalArg(nargs='?')):
		'''help: disable a service or an item in a list.
		name: name of the service or value of an item in a list
		item: item to be disabled, (not needed if name is a service)'''

		self.update(name, item, False)


	def update(self, name, item, state):
		state_to_str = lambda s: 'enabled' if s else 'disabled'

		if name in self.service_choices:
			config = Config()
			config.set(name + '.enabled', state)
		elif name in self.list_choices:
			if item is None:
				print('missing list item to be %s'%state_to_str(state))
				raise CommandError()

			item_list = self.get_item_list(name)
			if state == True:
				self.itemlist_call(item_list.enable, item)
			else:
				self.itemlist_call(item_list.disable, item)
			print('%s %s in %s list'%(item, state_to_str(state), item_list.name))
		else:
			print('unknown enable option: %s'%name)

