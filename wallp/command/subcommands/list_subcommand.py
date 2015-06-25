
from mutils.misc import colors

from ..subcommand import Subcommand, subcmd, Choices
from ...service import ServiceFactory 


class ListSubcommand(Subcommand):
	list_choices = Choices(['colors', 'services'], default=None)

	@subcmd
	def list(self, list_name=list_choices):
		'''Print built-in lists.
		list_name: name of the list'''

		if list_name == 'colors':
			self.list_colors()
		elif list_name == 'services':
			self.list_services()


	def list_colors(self):
		colors.print_names()


	def list_services(self):
		service_factory = ServiceFactory()
		for name, enabled in service_factory.services:
			print('{0:<15}: {1}'.format(name, 'enabled' if enabled else 'disabled'))

