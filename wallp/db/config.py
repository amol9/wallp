
from . import Setting
from .namevalueset import NameValueSet, NameError
from .singleton import Singleton
from .nv_shortcut_mixin import NVShortcutMixin


class ConfigError(NameError):
	nv_typename = 'setting'


class _Config(NVShortcutMixin, NameValueSet):
	nvtype = Setting
	name_err_type = ConfigError

	def __init__(self):
		super(_Config, self).__init__()


class Config(Singleton):
	classtype = _Config

