from abc import ABCMeta, abstractmethod

from redlib.api.misc import md5hash


class Source:
	__metaclass__ = ABCMeta

	name		= None
	params_cls 	= None
	online		= None
	db		= None
	gen		= None

	def get_image(self, params=None):
		pass

	def get_trace(self):
		pass


class SourceError(Exception):
	pass


class SourceParams:
	name = None

	def __init__(self, query=None, color=None):
		self.query	= query
		self.color	= color

		self.hash_params = ['query', 'color']


	def get_hash(self):
		s = ''
		for p in self.hash_params:
			value = getattr(self, p, None)
			if value is not None:
				s += str(value)
		return md5hash(s)

