from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import *
from ..globals import Const


#singleton
class __DBSession():
	def __init__(self):
		self._db_path = Const.db_path
		self._db_echo = True if Const.debug else False

	
	def init_db(self):
		self._engine = create_engine('sqlite:///' + self._db_path, echo=self._db_echo)
		self._session = sessionmaker(bind=engine)()


#interface for singleton
class DBSession():
	instance = None
	session_class = None

	def __init__(self, db_path=None):
		if DBSession.session_class is None:
			db_path = Const.db_path if db_path is None else db_path
			engine = create_engine('sqlite:///' + db_path, echo=Const.debug)
			DBSession.session_class = sessionmaker(bind=engine)

		if DBSession.instance is None:
			DBSession.instance = DBSession.session_class()


	def __getattr__(self, name):
		return getattr(DBSession.instance, name)
