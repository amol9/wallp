
class NVHelper:

	def __init__(self, group=None):
		self._prefix = (group + '.') if group is not None else ''


	def pget(self, name, default=None):
		try:
			return self.get(self._prefix + name)
		except self.name_err_type:
			self.padd(name, default)

		return default


	def pset(self, name, value):
		try:
			self.set(self._prefix + name, value)
		except self.name_err_type:
			self.padd(name, value)	


	def padd(self, name, value):
		self.add(self._prefix + name, value, type(value))
		self.commit()


	def eget(self, name, default=None):
		try:
			return self.get(name)
		except self.name_err_type:
			self.eadd(name, default)

		return default
	

	def eset(self, name, value):
		try:
			self.set(name, value)
		except self.name_err_type:
			self.eadd(name, value)	


	def eadd(self, name, value):
		self.add(name, value, type(value))
		self.commit()

