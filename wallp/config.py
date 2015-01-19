import system
if system.is_py3(): from configparser import ConfigParser
else: from ConfigParser import ConfigParser
from os.path import exists

from wallp.globals import Const

class Config():
	def __init__(self):
		self._config = ConfigParser()
		self._config_filepath = Const.config_filepath
		if exists(self._config_filepath):
			self._config.read(Const.config_filepath)


	def get(self, section, option, default=None):
		if self._config.has_section(section):
			if self._config.has_option(section, option):
				return self._config.get(section, option)
			else:
				if default is not None:
					self._config.set(section, option, self.csv_if_list(default))
		else:
			if default is not None:
				self._config.add_section(section)
				self._config.set(section, option, self.csv_if_list(default))

		return default


	def csv_if_list(self, value):
		if isinstance(value, list):
			value = ''.join([v + ', ' for v in value[0:-1]]) + value[-1]
			return value
		return value


	def get_list(self, section, option, default=None, sep=','):
		value = self.get(section, option, default)
		if value is not None and not isinstance(value, list):
			value = value.split(sep)
		return value


	def __del__(self):
		with open(self._config_filepath, 'w') as f:
			self._config.write(f)


config = Config()
	


