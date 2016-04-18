
from redcmd.api import Subcommand, subcmd


class ConfigSubcommand(Subcommand):

	@subcmd
	def config(self):
		'Manage configuration.'

