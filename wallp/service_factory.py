from random import choice

from wallp.bing import Bing
from wallp.imgur import Imgur
from wallp.google import Google
from wallp.reddit import Reddit
from wallp.bitmap import Bitmap
from wallp.deviantart import DeviantArt


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


	def get_all(self):
		return list(self._services.values())


	services = property(get_all)


service_factory = ServiceFactory()

service_factory.add(Bing.name, Bing)
service_factory.add(Bitmap.name, Bitmap)
service_factory.add(DeviantArt.name, DeviantArt)
service_factory.add(Google.name, Google)
service_factory.add(Imgur.name, Imgur)
service_factory.add(Reddit.name, Reddit)

