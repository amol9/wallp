from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from csv import reader
import os
from os.path import dirname, abspath, join as joinpath

from . import *
from ..globals import Const
from ..service import service_factory


class CreateDB():
	def __init__(self, db_path):
		self._engine = create_engine('sqlite:///' + db_path, echo=True)
		self._session = sessionmaker(bind=self._engine)()
		self._data_dir_abspath = joinpath(dirname(abspath(__file__)), 'data')


	def create_schema(self):
		try:
			Base.metadata.create_all(self._engine)
		except Exception as e:
			print('error in creating schema')
			raise Exception()


	def insert_data(self):
		self.insert_default_config()
		self.insert_imgur_data()
		self.insert_reddit_data()

	
	def insert_default_config(self):
		self.insert_service_status()
		self.insert_config_defaults()
		self._session.commit()


	def insert_service_status(self):
		for service in service_factory.get_all():
			print service.name
			self._session.add(Setting(group=service.name, name='enabled', value='true'))


	def insert_config_defaults(self):
		with open(joinpath(self._data_dir_abspath, 'config.csv'), 'r') as config_csv:
			config_reader = reader(config_csv)
			for row in config_reader:
				group, name = row[0].split('.')
				self._session.add(Setting(group=group, name=name, value=row[1]))



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

