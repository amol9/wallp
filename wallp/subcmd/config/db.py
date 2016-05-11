import os
from six.moves import input

from redcmd.api import Subcommand, subcmd, CommandError

from .base import ConfigSubcommand
from ... import const
from ...db.manage.db import DB, ManageDBError


__all__ = ['DbSubcommand']


class DbSubcommand(ConfigSubcommand):

	@subcmd
	def db(self):
		'Manage program database.'
		pass


class DbSubSubcommands(DbSubcommand):

	def __init__(self):
		self._db = DB()


	@subcmd
	def reset(self):
		'''Reset the database.
		**WARNING** all custom settings, image history, etc. will be lost.'''

		choice = input('WARNING: ALL CUSTOM SETTINGS, IMAGE HISTORY, ETC. WILL BE LOST.\n' +
				'Are you sure you want to reset the db? [y/N]: ')
		if choice == 'y':
			backup_db_path = self.exc_call(self._db.reset)
			print('database backup created: %s'%backup_db_path)
			print('database reset')


	@subcmd
	def backup(self, dest_dir=None):
		'''Backup the database.
		dest_dir: path to the directory where backup will be stored'''

		backup_db_path = self.exc_call(self._db.backup, dest_path=dest_dir)
		print('backup created: %s'%backup_db_path)


	def exc_call(self, method, *args, **kwargs):
		try:
			return method(*args, **kwargs)
		except ManageDBError as e:
			print(e)
			raise CommandError()

