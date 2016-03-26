
from .. import Setting
from ..namevalueset import NameValueSet, NameError

from redlib.api.misc import Singleton

from ..nv_shortcut_mixin import NVShortcutMixin


class ConfigError(NameError):
	nv_typename = 'setting'


class Config(NVShortcutMixin, NameValueSet):
	nvtype = Setting
	name_err_type = ConfigError

	def __init__(self, group=None):
		super(Config, self).__init__()

		self._prefix = (group + '.') if group is not None else ''


	def pget(self, name, default=None):
		try:
			return self.get(self._prefix + name)
		except ConfigError:
			self.padd(name, default)

		return default


	def pset(self, name, value):
		try:
			self.set(self._prefix + name, value)
		except ConfigError:
			self.padd(name, value)	


	def padd(self, name, value):
		self.add(self._prefix + name, value, type(value))
		self.commit()


	def eget(self, name, default=None):
		try:
			return self.get(name)
		except ConfigError:
			self.eadd(name, default)

		return default
	

	def eset(self, name, value):
		try:
			self.set(name, value)
		except ConfigError:
			self.eadd(name, value)	


	def eadd(self, name, value):
		self.add(name, value, type(value))
		self.commit()

