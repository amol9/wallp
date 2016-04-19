from random import choice

from redlib.api.misc import Singleton

from ..db.app.sources import Sources, DBSourceError
from ..util import log
from .base import Source
from .all_sources import *


class SourceFactoryError(Exception):
	pass


class _SourceFactory():
	def __init__(self):
		self._sources = {}
		self._status_loaded = False
		self.add_all_sources()


	def add_all_sources(self, cls=None):
		if cls is None:
			cls = Source

		for subcls in cls.__subclasses__():
			if subcls.name is not None:
				self.add(subcls)
			self.add_all_sources(cls=subcls)

	def add(self, source_class):
		self._sources[source_class.name] = source_class

	
	def load_status(self):
		if self._status_loaded:
			return

		db_sources = Sources()
		for source_name in self._sources.keys():
			try:
				enabled = db_sources.enabled(source_name)
				self._sources[source_name].enabled = enabled
			except DBSourceError as e:
				log.error(str(e))


	def get(self, source_name):
		if source_name is None:
			return self.get_random()

		self.load_status()

		source = self._sources.get(source_name, None)
		if source is not None:
			if not source.enabled:
				raise SourceFactoryError('%s is disabled, enable using >wallp config enable %s'%(2*(source_name,)))
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

