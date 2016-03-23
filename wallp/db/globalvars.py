
from redlib.api.misc import Singleton

from .var import Var
from .namevalueset import NameValueSet, NameError


class VarError(NameError):
	nv_typename = 'variable'


class _GlobalVars(NameValueSet):
	nvtype = Var
	name_err_type = VarError


class GlobalVars(Singleton):
	classtype = _GlobalVars

