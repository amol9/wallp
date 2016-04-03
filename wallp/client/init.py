import os
from os.path import exists
from six.moves import input

from ..db import DBError, NotFoundError
from ..db.app.config import Config, ConfigError
from ..db.create_db import CreateDB
from ..util import log
from .. import const


class InitError(Exception):
	pass


def db_exists():
	return exists(const.db_path)


def first_run():
	if not exists(const.data_dir):	
		os.mkdirs(const.data_dir)
		log.debug('data directory created')
		create_db()


def create_db():
	create_db = CreateDB()
	create_db.execute()
	log.debug('db created')
	

def start_log():
	try:
		if not db_exists():
			choice = input('Database not found.\nDo you want to create a fresh db? [Y/n]: ')
			if choice in ['Y', 'y', '']:
				create_db()
			else:
				raise InitError('Cannot continue without a database, quitting..')

		config = Config()
		log.start(config.get('client.logfile'), loglevel=config.get('client.loglevel'))

	except (DBError, ConfigError, NotFoundError) as e:
		print(str(e))
		print('continuing without logging')

