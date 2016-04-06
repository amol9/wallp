
from ..model.var import Var

from .kvhelper import KVHelper


class VarError(Exception):
	pass


class Vars(KVHelper):
	def __init__(self):	
		KVHelper.__init__(self, Var, VarError)

