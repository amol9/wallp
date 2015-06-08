from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from csv import reader
import os
from os.path import dirname, abspath, join as joinpath

from . import *
from ..globals import Const
from ..service import service_factory


class CreateDBError(Exception):
	pass


class CreateDB():
	def __init__(self, db_path):
		self._session = DBSession(db_path=db_path)
		self._data_dir_abspath = joinpath(dirname(abspath(__file__)), 'data')


	def execute(self):
		self.create_schema()
		try:
			self.insert_data()
		except IntegrityError as e:
			raise CreateDBError(str(e))


	def create_schema(self):
		Base.metadata.create_all(self._session.bind)


	def insert_data(self):
		self.insert_default_config()
		self.insert_imgur_data()
		self.insert_reddit_data()


	def insert_globalvars(self):
		with open(joinpath(self._data_dir_abspath, 'globalvars.csv'), 'r') as globalvars_csv:
			globalvars_reader = reader(globalvars_csv)
			globalvars = GlobalVars()
			for row in globalvars_reader:
				globalvars.add(row[0], eval(row[1]), row[2])

	
	def insert_default_config(self):
		config = Config()
		self.insert_service_status(config)
		self.insert_config_defaults(config)

		self._session.commit()


	def insert_service_status(self, config):
		for service in service_factory.get_all():
			config.add(service.name + '.enabled', True, bool)


	def insert_config_defaults(self, config):
		with open(joinpath(self._data_dir_abspath, 'config.csv'), 'r') as config_csv:
			config_reader = reader(config_csv)
			for row in config_reader:
				config.add(row[0], eval(row[1]), row[2])


	def insert_imgur_data(self):
		with open(joinpath(self._data_dir_abspath, 'imgur.csv'), 'r') as imgur_csv:
			imgur_reader = reader(imgur_csv)
			for row in imgur_reader:
				self._session.add(ImgurAlbum(url=row[0]))
		self._session.commit()


	def insert_reddit_data(self):
		with open(joinpath(self._data_dir_abspath, 'reddit.csv'), 'r') as reddit_csv:
			reddit_reader = reader(reddit_csv)
			for row in reddit_reader:
				self._session.add(Subreddit(name=row[0]))
		self._session.commit()

