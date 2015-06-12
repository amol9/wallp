

from .var import Var
from .namevalueset import NameValueSet, NameError
from .singleton import Singleton


class VarError(NameError):
	nv_typename = 'variable'


class _GlobalVars(NameValueSet):
	nvtype = Var
	name_err_type = VarError


class GlobalVars(Singleton):
	classtype = _GlobalVars

