
from ..subcommand import Subcommand, subcmd
from ...globals import Const
from ...db import CreateDB


class DbSubcommand(Subcommand):

	@subcmd
	def db(self):
		pass


class DbSubSubCommands(DbSubcommand):

	@subcmd
	def reset(self):
		choice = raw_input('Are you sure you want to reset the db? [y/N]:')
		if choice == 'y':
			db_path = Const.db_path
			os.remove(db_path)
			self.create_db()


	def create_db(self):
		create_db = CreateDB()
		create_db.execute()
		print('db created')


	@subcmd
	def backup(self, path):
		print('not implemented')

