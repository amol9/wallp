from os.path import dirname, join as joinpath, basename, abspath, exists
from os import makedirs
from shutil import copyfile
from datetime import datetime
import csv

from alembic.config import Config as AlConfig
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from sqlalchemy import String
from sqlalchemy.engine import reflection

from ... import const
from ..model.all import *
from ..dbsession import DBSession


class ManageDBError(Exception):
	pass


class DB:

	def __init__(self):
		pass


	def check(self):
		if not exists(const.db_path):
			self.create()


	def create(self):
		self.upgrade()
		self.insert_data()


	def insert_data(self):
		db_session = DBSession()
		inspector = reflection.Inspector.from_engine(db_session.bind)

		tables = [Config, Source, ImgurAlbum, Var, Subreddit, SearchTerm]
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
							value = value if col_cls == String else eval(value)	# convert if not string

							values[cols[i]] = value

						if any(map(lambda r : all([getattr(r, c) == values.get(c) for c in uniq_cols]), exst_rows)):
							continue	# already present

						record = table(**values)
						db_session.add(record)

			db_session.commit()


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


	def reset(self):
		pass
