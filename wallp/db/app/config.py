
from ..model.config import Config as ConfigModel

from .kvhelper import KVHelper


class ConfigError(Exception):
	pass


class Config(KVHelper):
	def __init__(self, group=None):	
		KVHelper.__init__(self, ConfigModel, ConfigError, prefix=group)

