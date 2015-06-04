from sqlalchemy import create_engine
from sqlalchemy. import sessionmaker

from . import *


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
		if self.session_class is None:
			db_path = Const.db_path if db_path is None else db_path
			engine = create_engine('sqlite:///' + db_path, Const.debug)
			self.session_class = sessionmaker(bind=engine)

		if self.instance is None:
			instance = self.session_class()


	def __getattr__(self, name):
		return getattr(self.instance, name)
