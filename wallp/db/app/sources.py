
from .. import DBSession
from .. import Source


class Sources:

	def __init__(self):
		pass


	def add(self, name, enabled=True):
		source = Source(name=name, enabled=enabled)
		# add


	def enabled(self, name):
		pass
	
