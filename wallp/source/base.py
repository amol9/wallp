from abc import ABCMeta, abstractmethod

from redlib.api.misc import md5hash


class Source:
	__metaclass__ = ABCMeta

	name	= None
	online	= None
	db	= None
	gen	= None

	def get_image(self, params=None):
		pass

	def get_trace(self):
		pass


class SourceError(Exception):
	pass


class SourceParams(object):
	name = None

	def __init__(self, query=None, color=None):
		self.query	= query
		self.color	= color

		self.hash_params = ['query', 'color']


	def get_hash(self):
		s = ''
		for p in self.hash_params:
			if getattr(self, p, None) is not None:
				s += p

		return md5hash(s)


class SourceResponse:

	def __init__(self, url=None, filepath=None, db_image=None, temp_filepath=None, ext=None):
		self.url		= url
		self.filepath		= filepath
		self.db_image		= db_image
		self.temp_filepath 	= temp_filepath
		self.ext		= None

		self.im_type		= None
		self.im_width		= None
		self.im_height		= None

