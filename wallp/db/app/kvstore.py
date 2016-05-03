
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound

from ...util import log
from ..dbsession import DBSession


class KVError(Exception):
	pass


class KeyNotFound(Exception):
	pass


class KVStore:

	def __init__(self, table):
		self._dbsession = DBSession()
		self._table = table


	def add(self, name, value):
		if value is None:
			svalue = None
			stype = None
		else:
			svalue = str(value)
			stype= type(value).__name__

		record = self._table(name=name, value=svalue, type=stype)
		self._dbsession.add(record)
		self.commit()


	def get(self, name):
		try:
			record = self._dbsession.query(self._table).filter(self._table.name == name).one()
		except (NoResultFound, OperationalError) as e:
			raise KeyNotFound(str(e))

		if record.value is None:
			return None

		vtype = eval(record.type)

		value = None
		if vtype == bool:
			value = True if value.lower() == 'true' else False
		else:
			value = vtype(record.value)

		return value


	def get_all(self):
		result = None
		try:
			result = self._dbsession.query(self._table).all()
		except OperationalError as e:
			log.error(e.orig)
			raise KVError()

		return map(lambda r : (r.name, r.value), result)


	def set(self, name, value, check_type=False):
		try:
			record = self._dbsession.query(self._table).filter(self._table.name == name).one()
		except (NoResultFound, OperationalError) as e:
			raise KeyNotFound(str(e))

		if value is None:
			record.value = None

		else:
			if check_type and record.type is not None:
				vtype = eval(record.type)

				if vtype != bool:
					try:
						vtype(value)
					except ValueError as e:
						raise KVError(str(e))
				else:
					if not value.lower() in ['true', 'false']:
						raise KVError('boolean value, must be true or false')

			else:
				record.type = type(value).__name__

			record.value = str(value)
			
		self.commit()


	def commit(self):
		try:
			self._dbsession.commit()
		except OperationalError as e:
			self._dbsession.rollback()
			raise KVError(str(e))

