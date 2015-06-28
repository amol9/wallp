from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import exists
import sys

from . import *
from ..globals import Const
from .exc import DBError
from ..util import log


class DBSession():
	'Singleton for sqlalchemy session.'

	instance = None
	session_class = None

	def __init__(self, db_path=None, create_db=False):
		if DBSession.session_class is None:
			db_path = Const.db_path if db_path is None else db_path
			if not create_db:
				if not exists(db_path):
					raise DBError('No database found.')

			engine = create_engine('sqlite:///' + db_path, echo=Const.debug)
			DBSession.session_class = sessionmaker(bind=engine)


		if DBSession.instance is None:
			DBSession.instance = DBSession.session_class()


	def __getattr__(self, name):
		return getattr(DBSession.instance, name)


	def close(self):
		self.instance.close()
		DBSession.instance = None
		DBSession.session_class = None

