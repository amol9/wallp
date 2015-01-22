from abc import ABCMeta, abstractmethod
from random import choice

from wallp.system import *

'''if is_py3():
	class Service(metaclass=ABCMeta):
		@abstractmethod
		def get_image(pictures_dir, basename, query=None, color=None):
			pass

else:'''
class Service():
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_image(pictures_dir, basename, query=None, color=None):
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
		service = choice(list(self._services.values()))
		return service()


	def get_services(self):
		return list(self._services.values())


	services = property(get_services)


service_factory = ServiceFactory()
		

