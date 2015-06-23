
from ..subcommand import Subcommand, subcmd, Choices
from ...client import Client, ChangeWPError
from ..exc import CommandError
from ...util import log
from ...service import ServiceFactory


class ChangeSubcommand(Subcommand):
	service_choices = Choices([name for name, _ in ServiceFactory().services], opt=True)
	
	@subcmd
	def change(self, service=service_choices, query=None, color=None):
		'''help: change the wallpaper
		service: service name to get the wallpaper from
		query: search term, specify multiple words by enclosing them in quotes
		color: preferred color'''

		client = Client(service_name=service, query=query, color=color)
		try:
			client.change_wallpaper()
		except ChangeWPError as e:
			log.error(str(e))
			raise CommandError()

