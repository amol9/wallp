
from ..subcommand import Subcommand, subcmd

class DbSubcommand(Subcommand):

	@subcmd
	def db(self):
		pass


class DbSubSubCommands(DbSubcommand):

	@subcmd
	def reset(self):
		'Reset the database. WARNING: This will ....'
		pass


	@subcmd
	def backup(self, path):
		'Backup the database.'
		pass

