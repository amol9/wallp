
from ..subcommand import Subcommand, subcmd
from ...client import Client, ChangeWPError


class ChangeSubcommand(Subcommand):
	
	@subcmd
	def change(self, service=None, query=None, color=None):
		client = Client(service_name=service, query=query, color=color)
		try:
			client.change_wallpaper()
		except ChangeWPError as e:
			log.error(str(e))
			raise AppError()

