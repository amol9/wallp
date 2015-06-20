from random import randint

from ..db import func as dbfunc
from ..util import log
from ..service import ServiceError


class ImageUrlsMixin:
	def __init__(self):
		self._image_urls = None


	def select_url(self, image_urls):
		self._image_urls = image_urls
		image_count = len(self._image_urls)

		if image_count == 0:
			raise ServiceError()

		log.debug('%d image urls found'%image_count)

		image_url = None

		while len(self._image_urls) > 0:
			rindex = randint(0, len(self._image_urls) - 1)
			image_url = self._image_urls[rindex]

			if dbfunc.image_url_seen(image_url):
				del self._image_urls[rindex]
			else:
				self.add_trace_step('selected random url', image_url)
				break

		return image_url, image_count
			
		
