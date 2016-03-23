
from redcmd.api import Subcommand, subcmd, Arg, CommandError

from ..client import Client, ChangeWPError
from ..util import log
from ..service import ServiceFactory


__all__ = ['ChangeSubcommand']


class ChangeSubcommand(Subcommand):
	
	@subcmd
	def change(self, service=Arg(choices=ServiceFactory().service_names, opt=True), query=None, color=None):
		'''Change the wallpaper.
		service: 	service name to get the wallpaper from
		query: 		search term, specify multiple words by enclosing them in quotes
		color: 		preferred color'''

		client = Client(service_name=service, query=query, color=color)
		try:
			client.change_wallpaper()
		except ChangeWPError as e:
			log.error(str(e))
			raise CommandError()

