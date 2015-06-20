from random import randint

from ..db import func as dbfunc
from ..util import log
from ..service import ServiceError


class ImageUrlsMixin(object):
	def __init__(self):
		super(ImageUrlsMixin, self).__init__()
		self._image_urls = None
		self._image_count = None


	def add_urls(self, image_urls):
		if len(image_urls) == 0:
			raise ServiceError()
		self._image_urls = image_urls
		self._image_count = len(image_urls)


	def select_url(self):
		if len(self._image_urls) == 0:
			raise ServiceError()

		image_url = None

		while len(self._image_urls) > 0:
			rindex = randint(0, len(self._image_urls) - 1)
			image_url = self._image_urls[rindex]

			del self._image_urls[rindex]

			if dbfunc.image_url_seen(image_url):
				continue
			else:
				break

		return image_url
			
