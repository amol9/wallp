import system
if system.is_py3(): from configparser import ConfigParser
else: from ConfigParser import ConfigParser

from wallp.globals import Const

class Config():
	def __init__(self):
		self._config = ConfigParser()
		self._config.read(Const.config_filename)


	def get(self, section, setting):
		return self._config.get(section, setting)


	def get_list(self, section, setting, sep=','):
		value = self._config.get(section, setting)
		print 'value: ', value
		return value.split(sep)


config = Config()
	


