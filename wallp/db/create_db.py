from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from csv import reader
import os
from os.path import dirname, abspath, join as joinpath

from . import *
from ..globals import Const


class CreateOp():
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
		pass


	def insert_imgur_data(self):
		with open(joinpath(self._data_dir_abspath, 'imgur.csv'), 'r') as imgur_csv:
			imgur_reader = reader(imgur_csv)
			for row in imgur_reader:
				self._session.add(Imgur(album=row[0]))
		self._session.commit()


	def insert_reddit_data(self):
		with open(joinpath(self._data_dir_abspath, 'reddit.csv'), 'r') as reddit_csv:
			reddit_reader = reader(reddit_csv)
			for row in reddit_reader:
				self._session.add(Reddit(sub=row[0]))
		self._session.commit()


def create_db(db_path):
	co = CreateOp(db_path)
	co.create_schema()
	co.insert_data()

