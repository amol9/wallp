from abc import ABCMeta, abstractmethod
from random import choice


class Service():
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_image(pictures_dir, basename, choice=None):
		pass


class ServiceException(Exception):
	pass


class ServiceFactory():
	def __init__(self):
		self._services = {}
	
	
	def add(self, service_name, service_class):
		self._services[service_name] = service_class


	def get(self, service_name):
		service = self._services.get(service_name, None)
		if service:
			return service()
		return None


	def get_random(self):
		service = choice(self._services.values())
		return service()


service_factory = ServiceFactory()
		

