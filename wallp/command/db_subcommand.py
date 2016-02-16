import os
from six.moves import input

from redcmd.api import Subcommand, subcmd

from ..globals import Const
from ..db.create_db import CreateDB
from ..db import DBSession


class DbSubcommand(Subcommand):

	@subcmd
	def db(self):
		'Database commands.'
		pass


class DbSubSubCommands(DbSubcommand):

	@subcmd
	def reset(self):
		'''Reset the database.
		**WARNING** all custom settings, image history, etc. will be lost.'''

		choice = input('Are you sure you want to reset the db? [y/N]: ')
		if choice == 'y':
			db_path = Const.db_path
			dbsession = DBSession()
			dbsession.close()

			os.remove(db_path)
			self.create_db()


	def create_db(self):
		create_db = CreateDB()
		create_db.execute()
		print('db created')


	@subcmd
	def backup(self, path):
		'''Backup the database.
		path: path to the directory or the file where backup will be stored'''

		print('not implemented')


	@subcmd
	def restore(self, path):
		'''Restore the database.
		path: path to the database backup file to restore from'''

		print('not implemented')

