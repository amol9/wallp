from random import choice

from redlib.api.misc import Singleton

from ..db import Config, ConfigError
from ..util import log
from .all_sources import *


class SourceFactoryError(Exception):
	pass


class _SourceFactory():
	def __init__(self):
		self._sources = {}
		self._status_loaded = False


	def add_all_sources(self):
		for source_class in Source.__subclasses__:
			if source_class.name is not None:
				self.add(source_class)

	def add(self, source_class):
		self._sources[source_class.name] = source_class

	
	def load_status(self):
		if self._status_loaded:
			return
		config = Config()
		for source_name in self._sources.keys():
			try:
				enabled = config.get(source_name + '.enabled')
				self._sources[source_name].enabled = enabled
			except ConfigError as e:
				log.error(str(e))


	def get(self, source_name):
		if source_name is None:
			return self.get_random()

		self.load_status()

		source = self._sources.get(source_name, None)
		if source is not None:
			if not source.enabled:
				raise SourceFactoryError('%s is disabled'%source_name)
			return source()


	def get_random(self):
		self.load_status()

		enabled_sources = [s for s in self._sources.values() if s.enabled]
		if len(enabled_sources) == 0:
			raise SourceFactoryError('all sources have been disabled')

		source= choice(enabled_sources)
		return source()


	def get_all(self):
		self.load_status()

		return list([(name, info.enabled) for (name, info) in  self._sources.items()])


	def get_source_names(self):
		return list(self._sources.keys())


	sources = property(get_all)
	source_names = property(get_source_names)


class SourceFactory(Singleton):
	classtype = _SourceFactory

