import os
from six.moves import input

from redcmd.api import Subcommand, subcmd

from .. import const
from ..db.dbsession import DBSession
from ..db.manage.db import DB


__all__ = ['DbSubcommand']


class DbSubcommand(Subcommand):

	@subcmd
	def db(self):
		'Database commands.'
		pass


class DbSubSubCommands(DbSubcommand):

	def __init__(self):
		self._db = DB()


	@subcmd
	def reset(self):
		'''Reset the database.
		**WARNING** all custom settings, image history, etc. will be lost.'''

		choice = input('Are you sure you want to reset the db? [y/N]: ')
		if choice == 'y':
			self._db.reset()


	@subcmd
	def backup(self, path):
		'''Backup the database.
		path: path to the directory or the file where backup will be stored'''

		self._db.backup()


	@subcmd
	def restore(self, path):
		'''Restore the database.
		path: path to the database backup file to restore from'''

		print('not implemented')


	@subcmd
	def upgrade(self):
		'Upgrade the database to latest version.'

		self._db.upgrade()
		self._db.insert_data()

