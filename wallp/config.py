import system
if system.is_py3(): from configparser import ConfigParser
else: from ConfigParser import ConfigParser

from wallp.globals import Const

class Config():
	def __init__(self):
		self._config = ConfigParser()
		if exists(Const.config_filepath):
			self._config.read(Const.config_filepath)


	def get(self, section, option, dafault=None):
		value = self._config.get(section, option)

		if self._config.has_section(section):
			if self._config.has_option(option):
				return self._config.get(section, option)
			else:
				if default is not None:
					self._config.set(section, option, default)
		else:
			if default is not None:
				self._config.add_section(section)
				self._config.set(section, option, default)
		return default


	def get_list(self, section, option, default=None, sep=','):
		value = self.get(section, option, default)
		return value.split(sep) if value is not None else None


	def __del__(self):
		with open(Const.config_filepath, 'w') as f:
			self._config.write(f)


config = Config()
	


