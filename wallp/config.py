from mutils.system import *
if is_py3():
	from configparser import ConfigParser
else:
	from ConfigParser import ConfigParser
from os.path import exists

from wallp.globals import Const


class Config():
	def __init__(self):
		self._config = ConfigParser()
		self._config_filepath = Const.config_filepath
		if exists(self._config_filepath):
			self._config.read(Const.config_filepath)


	def get(self, section, option, default=None, type=None):
		ret = default
		if self._config.has_section(section):
			if self._config.has_option(section, option):
				ret = self._config.get(section, option)
			else:
				if default is not None:
					self._config.set(section, option, self.csv_if_list(default))
					self.write()
		else:
			if default is not None:
				self._config.add_section(section)
				self._config.set(section, option, self.csv_if_list(default))
				self.write()

		return self.typecast(ret, type)


	def set(self, section, option, value):
		if not self._config.has_section(section):
			self._config.add_section(section)

		self._config.set(section, option, value)
		self.write()


	def typecast(self, value, type):
		if type is None:
			return value

		if type == bool:
			if value in ['False', 'false', 'No', 'no', 'N', 'n', '0']:
				return False
			else:
				return True
		return value


	def csv_if_list(self, value):
		if isinstance(value, list):
			value = ''.join([v + ', ' for v in value[0:-1]]) + value[-1]
			return value
		return str(value)


	def get_list(self, section, option, default=None, sep=','):
		value = self.get(section, option, default)
		if value is not None and not isinstance(value, list):
			value = value.split(sep)
		return value


	def write(self):
		with open(self._config_filepath, 'w') as f:
			self._config.write(f)


config = Config()
	


