from os.path import dirname, join as joinpath, basename, abspath, exists
from os import makedirs
from shutil import copyfile
from datetime import datetime
import csv

from alembic.config import Config as AlConfig
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext

from ... import const
from ..model.all import *


class ManageDBError(Exception):
	pass


class DB:

	def __init__(self):
		pass


	def create(self):
		self.upgrade()


	def insert_data(self):
		db_session = DBSession()
		tables = [Source, ImgurAlbum]

		data_dir_path = joinpath(dirname(abspath(__file__)), 'data')

		for table in tables:
			data_file_path = joinpath(data_dir_path, table.__tablename__ + '.csv')

			if exists(data_file_path):
				with open(data_file_path, 'r') as f:
					csv_file = csv.reader(f)

					csv_cols = row[0]
					cols = []
					values = {}
					for row in csv_file:
						if csv_file.line_num == 1:
							cols = row
							values = dict.fromkeys(cols, None)

						for i in range(0, len(cols)):
							values[cols[i]] = row[i]

						record = table(**values)

						#if not exists row:	# or pass the constraint exception
						db_session.add(record)

			db_session.commit()

		# handle exceptions

		# if yes, load it as csv
		# if a column type != String, eval it
		# insert data


	def upgrade(self, script_location=None, db_path=None, dest_rev=None):
		script_location	= script_location or joinpath(dirname(abspath(__file__)), 'migrate')
		db_path 	= db_path or const.db_path
		dest_rev	= dest_rev or 'head'

		if not exists(dirname(db_path)):
			makedirs(dirname(db_path))

		sa_url = 'sqlite:///' + db_path

		config = AlConfig()
		config.set_main_option('script_location', script_location)
		config.set_main_option('sqlalchemy.url', sa_url)

		config.config_file_name = joinpath(dirname(script_location), 'alembic.ini')

		script = ScriptDirectory.from_config(config)

		def upgrade(rev, context):
			return script._upgrade_revs(dest_rev, rev)

		with EnvironmentContext(
			config,
			script,
			fn		= upgrade,
			as_sql		= False,
			starting_rev	= None,
			destination_rev	= dest_rev,
			tag		= None
		):
			script.run_env()


	def backup(self, dest_path=None):
		if dest_path is None:
			dest_path = dirname(const.db_path)

		db_path = const.db_path

		dt = datetime.now().strftime('%d_%b_%Y_%H_%M_%S').lower()
		dest_db_path = joinpath(dest_path, dt + '_' + basename(db_path))

		try:
			copyfile(db_path, dest_db_path)
		except (IOError, OSError) as e:
			raise ManageDBError(str(e))

		return dest_db_path


	def restore(self, src_path=None):
		pass


