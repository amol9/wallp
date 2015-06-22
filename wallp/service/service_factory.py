from random import choice

from .bing import Bing
from .imgur import Imgur
from .google import Google
from .reddit import Reddit
from .bitmap import Bitmap
from .deviantart import DeviantArt
from ..db import Config, ConfigError
from ..db.singleton import Singleton
from ..util import log


class ServiceInfo:
	def __init__(self, service_class, enabled):
		self.service_class = service_class
		self.enabled = enabled


class ServiceDisabled(Exception):
	pass


class NoEnabledServices(Exception):
	pass


class _ServiceFactory():
	def __init__(self):
		self._services = {}
		self.add(Bing.name, Bing)
		self.add(Bitmap.name, Bitmap)
		self.add(DeviantArt.name, DeviantArt)
		self.add(Google.name, Google)
		self.add(Imgur.name, Imgur)
		self.add(Reddit.name, Reddit)

	
	def add(self, service_name, service_class):
		config = Config()
		enabled = False
		try:
			enabled = config.get(service_name + '.enabled')
		except ConfigError as e:
			log.error(str(e))

		self._services[service_name] = ServiceInfo(service_class, enabled)


	def get(self, service_name):
		config = Config()
		enabled = False
		try:
			enabled = config.get(service_name + '.enabled')
		except ConfigError as e:
			log.error(str(e))
			raise ServiceDisabled()

		if not enabled:
			raise ServiceDisabled()

		service = self._services.get(service_name, None)
		if service:
			return service.service_class()
		return None


	def get_random(self):
		enabled_services = [s for s in self._services.values() if s.enabled]
		if len(enabled_services) == 0:
			raise NoEnabledServices()

		service = choice(enabled_services)
		return service.service_class()


	def get_all(self):
		return list([(name, info.enabled) for (name, info) in  self._services.items()])


	services = property(get_all)


class ServiceFactory(Singleton):
	classtype = _ServiceFactory
