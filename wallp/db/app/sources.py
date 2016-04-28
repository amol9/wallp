
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound

from ..dbsession import DBSession
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
		self.set_state(name, True)


	def disable(self, name):
		self.set_state(name, False)


	def set_state(self, name, state):
		try:
			self._db_session.query(Source).filter(Source.name == name).update({'enabled': state})
			self._db_session.commit()
		except (NoResultFound, OperationalError) as e:
			raise DBSourceError(str(e))


	def get_all(self):
		try:
			result = self._db_session.query(Source).all()
			return map(lambda r : (r.name, r.enabled), result)
		except (NoResultFound, OperationalError) as e:
			raise DBSourceError(str(e))

