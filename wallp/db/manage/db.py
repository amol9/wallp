from os.path import dirname, join as joinpath, basename, abspath, exists, isdir
from os import makedirs, remove
from shutil import copyfile
from datetime import datetime
import csv
import logging
import warnings

from alembic.config import Config as AlConfig
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from alembic.migration import MigrationContext
from sqlalchemy import String, update
from sqlalchemy.engine import reflection
from sqlalchemy.exc import OperationalError

from ... import const
from ..model.all import *
from ..dbsession import DBSession
from ...version import __version__


class ManageDBError(Exception):
	pass


class DBLogHandler(logging.Handler):

	def __init__(self):
		logging.Handler.__init__(self)
		self._file = open(const.db_logfile, 'a')


	def emit(self, record):
		self._file.write(self.format(record) + '\n')


class DB:
	script_location = joinpath(dirname(abspath(__file__)), 'migrate')

	def __init__(self):
		pass

	def check(self):
		response = None

		if not exists(const.db_path):
			self.upgrade()
			response = 'database created'
		else:
			db_session = DBSession()
			context = MigrationContext.configure(db_session.bind)
			cur_rev = context.get_current_revision()

			config_filepath = joinpath(dirname(self.script_location), 'alembic.ini')
			config = AlConfig(file_=config_filepath)
			config.set_main_option('script_location', self.script_location)
			script = ScriptDirectory.from_config(config)
			head_rev = script.get_current_head()

			if cur_rev != head_rev:
				self.backup()
				self.upgrade()
				response = 'database upgraded'

		self.insert_data()
		return response

	def create(self):
		self.upgrade()
		self.insert_data()


	def insert_data(self):
		db_session = DBSession()
		inspector = reflection.Inspector.from_engine(db_session.bind)

		tables = [Config, Source, ImgurAlbum, Var, Subreddit, Query]
		data_dir_path = joinpath(dirname(abspath(__file__)), 'data')

		for table in tables:
			data_file_path = joinpath(data_dir_path, table.__tablename__ + '.csv')

			if exists(data_file_path):
				with open(data_file_path, 'r') as f:
					csv_file = csv.reader(f)

					check_uniq = True
					exst_rows = []		# existing rows in table (to check against duplicate insertion)
					uniq_cols = []		# columns belonging to unique constraint
					uniq_cons = inspector.get_unique_constraints(table.__tablename__)
					if len(uniq_cons) == 0:
						check_uniq = False
					else:
						uniq_cols = uniq_cons[0]['column_names']	# only taking the first unique constraint (good for now)
						exst_rows = db_session.query(table).all()

					cols = []		# columns in data file
					values = {}
					for row in csv_file:
						if csv_file.line_num == 1:		# first row always has the column names
							cols = [c.strip() for c in row]
							values = dict.fromkeys(cols, None)
							continue

						for i in range(0, len(cols)):
							col_cls = getattr(table, cols[i]).type.__class__
							value = row[i].strip()
							if value == 'None':
								value = None
							else:
								value = value if col_cls == String else eval(value)	# convert if not string

							values[cols[i]] = value

						if any(map(lambda r : all([getattr(r, c) == values.get(c) for c in uniq_cols]), exst_rows)):
							continue	# already present

						record = table(**values)
						db_session.add(record)

			db_session.commit()

		self.update_app_version()


	def update_app_version(self):
		db_session = DBSession()
		try:
			db_session.execute(update(Var).where(Var.name == 'app_version').values(value=__version__))
			db_session.commit()
		except OperationalError as e:
			log.error(e)


	def upgrade(self, script_location=None, db_path=None, dest_rev=None):
		script_location	= script_location or self.script_location 
		db_path 	= db_path or const.db_path
		dest_rev	= dest_rev or 'head'

		if not exists(dirname(db_path)):
			makedirs(dirname(db_path))

		sa_url = 'sqlite:///' + db_path

		config_filepath = joinpath(dirname(script_location), 'alembic.ini')
		config = AlConfig(file_=config_filepath)

		config.set_main_option('script_location', script_location)
		config.set_main_option('sqlalchemy.url', sa_url)


		script = ScriptDirectory.from_config(config)

		warnings.filterwarnings('ignore', category=UserWarning, module='.*alembic.*')

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
		else:
			if not isdir(dest_path):
				raise ManageDBError('%s is not a valid directory'%dest_path)

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


	def reset(self):
		db_session = DBSession()
		db_session.close()

		backup_db_path = self.backup()

		db_path = const.db_path
		remove(db_path)

		self.upgrade()
		self.insert_data()

		return backup_db_path

