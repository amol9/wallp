from random import choice

from .bing import Bing
from .imgur import Imgur
from .google import Google
from .reddit import Reddit
from .bitmap import Bitmap
from .deviantart import DeviantArt
from .favorites import Favorites

from ..db import Config, ConfigError
from ..db.singleton import Singleton
from ..util import log


class ServiceInfo:
	def __init__(self, service_class, enabled=False):
		self.service_class = service_class
		self.enabled = enabled


class ServiceDisabled(Exception):
	pass


class NoEnabledServices(Exception):
	pass


class _ServiceFactory():
	def __init__(self):
		self._services = {}
		self.add(Bing)
		self.add(Bitmap)
		self.add(DeviantArt)
		self.add(Google)
		self.add(Imgur)
		self.add(Reddit)
		self.add(Favorites)

		self._status_loaded = False


	def add(self, service_class):
		self._services[service_class.name] = ServiceInfo(service_class)

	
	def load_status(self):
		if self._status_loaded:
			return
		config = Config()
		for service_name in self._services.keys():
			try:
				enabled = config.get(service_name + '.enabled')
				self._services[service_name].enabled = enabled
			except ConfigError as e:
				log.error(str(e))


	def get(self, service_name):
		self.load_status()

		service_info = self._services.get(service_name, None)
		if service_info is not None:
			if not service_info.enabled:
				raise ServiceDisabled()
			return service_info.service_class()


	def get_random(self):
		self.load_status()

		enabled_services = [s for s in self._services.values() if s.enabled]
		if len(enabled_services) == 0:
			raise NoEnabledServices()

		service_info = choice(enabled_services)
		return service_info.service_class()


	def get_all(self):
		self.load_status()

		return list([(name, info.enabled) for (name, info) in  self._services.items()])


	def get_service_names(self):
		return list(self._services.keys())


	services = property(get_all)
	service_names = property(get_service_names)


class ServiceFactory(Singleton):
	classtype = _ServiceFactory

