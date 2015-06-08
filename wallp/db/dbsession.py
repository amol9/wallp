from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import *
from ..globals import Const


class DBSession():
	'Singleton for sqlalchemy session.'

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
