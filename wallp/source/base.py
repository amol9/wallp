from abc import ABCMeta, abstractmethod


class Source:
	__metaclass__ = ABCMeta

	name	= None
	online	= None
	db	= None
	gen	= None

	def get_image(self, params=None):
		pass


class SourceError(Exception):
	pass


class SourceParams:
	name = None

	def __init__(self, query=None, color=None):
		self.query	= query
		self.color	= color


class SourceResponse:

	def __init__(self, url=None, filepath=None, db_image=None, temp_filepath=None):
		self.url		= url
		self.filepath		= filepath
		self.db_image		= db_image
		self.temp_filepath 	= temp_filepath

