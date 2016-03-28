
from redcmd.api import Subcommand, subcmd, Arg, CommandError

from .list_mixin import ListMixin
from ..source.source_factory import SourceFactory
from ..db.app.config import Config


__all__ = ['EnableSubcommands']


class EnableSubcommands(Subcommand, ListMixin):
	source_choices = SourceFactory().source_names
	name_choices = ListMixin.list_choices + source_choices
	
	@subcmd
	def enable(self, name=Arg(choices=name_choices, default=None), item=Arg(pos=True, nargs='?')):
		'''Enable a source or an item in a list.
		name: name of the source or value of an item in a list
		item: item to be enabled, (not needed if name is a source)'''

		self.update(name, item, True)


	@subcmd
	def disable(self, name=Arg(choices=name_choices, default=None), item=Arg(pos=True, nargs='?')):
		'''Disable a source or an item in a list.
		name: name of the source or value of an item in a list
		item: item to be disabled, (not needed if name is a source)'''

		self.update(name, item, False)


	def update(self, name, item, state):
		state_to_str = lambda s: 'enabled' if s else 'disabled'

		if name in self.source_choices:
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

