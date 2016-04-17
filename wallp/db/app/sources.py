
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound

from .. import DBSession
from ..model.source import Source


class DBSourceError(Exception):
	pass


class Sources:

	def __init__(self):
		self._db_session = DBSession()


	def add(self, name, enabled=True):
		source = Source(name=name, enabled=enabled)


	def enabled(self, name):
		try:
			record = self._db_session.query(Source).filter(Source.name == name).one()
			return record.enabled
		except (NoResultFound, OperationalError) as e:
			return False


	def enable(self, name):
		self.set_state(self, name, True)

	def disable(self, name):
		self.set_state(self, name, False)


	def set_state(self, name, state):
		try:
			self._db_session.query(Source).update({'enabled': state}).where(Source.name == name)
		except (NoResultFound, OperationalError) as e:
			raise DBSourceError(str(e))

