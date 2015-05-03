from sqlalchemy import create_engine
from sqlalchemy. import sessionmaker

from . import *


#singleton
class __Access():
	def __init__(self):
		self._db_path = Const.db_path
		self._db_echo = True if Const.debug else False

	
	def init_db(self):
		self._engine = create_engine('sqlite:///' + self._db_path, echo=self._db_echo)
		self._session = sessionmaker(bing=engine)()

	
	def get_config(self, setting):


	def set_config(self, setting, value):


	def add_imgur_album(self, url):


	def get_random_imgur_album(self):


	def add_reddit_sub(self, sub):


	def get_random_reddit_sub(self):


	def add_search_term(self, term):


	def get_random_search_term(self):




#interface for singleton
class Access():
	instance = None

	def __init__(self):
		if Access.instance is None:
			instance = __Access()
			instance.init_db()


	def __getattr__(self, name):
		return getattr(self.instance, name)
