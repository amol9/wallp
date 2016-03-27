
from redlib.api.misc import Singleton

from ..nv_shortcut_mixin import NVShortcutMixin
from ..setting import Setting
from ..namevalueset import NameValueSet, NameError
from .nvhelper import NVHelper


class ConfigError(NameError):
	nv_typename = 'setting'


class Config(NVShortcutMixin, NameValueSet, NVHelper):
	nvtype = Setting
	name_err_type = ConfigError

	def __init__(self, group=None):
		super(Config, self).__init__()
		NVHelper.__init__(self, group=group)

