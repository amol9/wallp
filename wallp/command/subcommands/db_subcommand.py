
from ..subcommand import Subcommand, subcmd
from ...globals import Const
from ...db.create_db import CreateDB


class DbSubcommand(Subcommand):

	@subcmd
	def db(self):
		'help: database commands'
		pass


class DbSubSubCommands(DbSubcommand):

	@subcmd
	def reset(self):
		'help: reset the database, **WARNING** all custom settings, image history, etc. will be lost'

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
		'''help: backup the database
		path: path to the directory or the file where backup will be stored'''

		print('not implemented')

