
from redlib.api.prnt import print_colorlist
from redcmd.api import Subcommand, subcmd, Arg

from ..source.source_factory import SourceFactory 


__all__ = ['ListSubcommand']


class ListSubcommand(Subcommand):	

	@subcmd
	def list(self, list_name=Arg(choices=['colors', 'sources'], default=None)):
		'''Print built-in lists.
		list_name: name of the list'''

		if list_name == 'colors':
			self.list_colors()
		elif list_name == 'sources':
			self.list_sources()


	def list_colors(self):
		print_colorlist()


	def list_sources(self):
		source_factory = SourceFactory()
		for name, enabled in source_factory.sources:
			print('{0:<15}: {1}'.format(name, 'enabled' if enabled else 'disabled'))

