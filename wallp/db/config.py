
from . import Setting
from .namevalueset import NameValueSet, NameError
from .singleton import Singleton


class ConfigError(NameError):
	nv_typename = 'setting'


class _Config(NameValueSet):
	nvtype = Setting
	name_err_type = ConfigError


class Config(Singleton):
	classtype = _Config

