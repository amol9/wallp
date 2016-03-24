
from ..db import Config, ConfigError


class ConfigMixin(object):

	def __init__(self):
		self._prefix = self.name + '.'
		self._config = Config()


	def config_get(self, name):
		return self._config.get(self._prefix + name)


	def config_set(self, name, value):
		try:
			self._config.set(self._prefix + name, value)
		except ConfigError:
			self.config_add(name, value)	

	def config_add(self, name, value):
		self._config.add(self._prefix + name, value, type(value))
		self._config.commit()


	def config_get_other(self, name):
		return self._config.get(name)

