

from .var import Var
from .namevalueset import NameValueSet, NameError
from .singleton import Singleton


class VarError(NameError):
	nv_typename = 'var'


class _GlobalVars(NameValueSet):
	nvtype = var
	name_err_type


class GlobalVars(Singleton):
	classtype = _GlobalVars

