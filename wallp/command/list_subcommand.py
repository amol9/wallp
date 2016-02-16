
from redlib.api.prnt import print_colorlist
from redcmd.api import Subcommand, subcmd, Arg

from ..service import ServiceFactory 


class ListSubcommand(Subcommand):	

	@subcmd
	def list(self, list_name=Arg(choices=['colors', 'services'], default=None)):
		'''Print built-in lists.
		list_name: name of the list'''

		if list_name == 'colors':
			self.list_colors()
		elif list_name == 'services':
			self.list_services()


	def list_colors(self):
		print_colorlist()


	def list_services(self):
		service_factory = ServiceFactory()
		for name, enabled in service_factory.services:
			print('{0:<15}: {1}'.format(name, 'enabled' if enabled else 'disabled'))

