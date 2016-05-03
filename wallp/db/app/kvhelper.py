
from .kvstore import KVStore, KVError, KeyNotFound


class KVHelper(KVStore):

	def __init__(self, table, err_type, prefix=None):
		KVStore.__init__(self, table)

		self._prefix = (prefix + '.') if prefix is not None else ''
		self._err_type = err_type


	def pget(self, name, default=None):
		try:
			return self.exc_call(self.get, self._prefix + name)
		except KeyNotFound:
			self.exc_call(self.add, self._prefix + name, default)

		return default


	def pset(self, name, value):
		try:
			self.exc_call(self.set, self._prefix + name, value)
		except KeyNotFound:
			self.exc_call(self.add, self._prefix + name, value)	


	def eget(self, name, default=None):
		try:
			return self.exc_call(self.get, name)
		except KeyNotFound:
			self.exc_call(self.add, name, default)

		return default
	

	def eset(self, name, value):
		try:
			self.exc_call(self.set, name, value)
		except KeyNotFound:
			self.exc_call(self.add, name, value)


	def sget(self, name):
		try:
			return self.get(name)
		except KeyNotFound as e:
			raise self._err_type('not found')


	def sset(self, name, value, **kwargs):
		try:
			return self.set(name, value, **kwargs)
		except KeyNotFound as e:
			raise self._err_type('not found')
		except KVError as e:
			raise self._err_type(str(e))


	def exc_call(self, method, *args):
		try:
			return method(*args)
		except KVError as e:
			raise self._err_type(str(e))

