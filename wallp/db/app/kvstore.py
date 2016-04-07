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
		svalue = str(value) if value is not None else None
		record = self._table(name=name, value=svalue, type=type(value).__name__)
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
			value = bool(eval(record.value))	#fix for bool
		else:
			value = vtype(record.value)

		return value


	def get_all_names(self):
		result = None
		try:
			result = self._dbsession.query(self._table).all()
		except OperationalError as e:
			log.error(e.orig)
			raise KVError()

		names = []
		for r in result:
			names.append(r.name)

		return names


	def set(self, name, value):
		try:
			record = self._dbsession.query(self._table).filter(self._table.name == name).one()
		except (NoResultFound, OperationalError) as e:
			raise KeyNotFound(str(e))

		if value is None:
			record.value = None

		else:
			vtype = eval(record.type)

			try:
				vtype(value)
			except ValueError as e:
				raise KVError(str(e))

			record.value = str(value)

		self.commit()


	def commit(self):
		try:
			self._dbsession.commit()
		except OperationalError as e:
			self._dbsession.rollback()
			raise KVError(str(e))

	names = property(get_all_names)

