from random import randint

from ..db import func as dbfunc
from ..util import log
from ..service import ServiceError


class ImageUrlsMixin(object):
	def __init__(self):
		super(ImageUrlsMixin, self).__init__()
		self._image_urls = []
		self._image_count = None
		self._image_info = {}

	def add_urls(self, image_urls):
		if len(image_urls) == 0:
			raise ServiceError()
		self._image_urls += image_urls
		self._image_count = len(image_urls)


	def add_url(self, image_url, image_source_info):
		self._image_urls.append(image_url)
		self._image_info[image_url] = image_source_info


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
				self.add_trace_step('selected url', image_url)
				log.debug('selected url: %s'%image_url)
				self._image_source = self._image_info.get(image_url, None)

				import pdb; pdb.set_trace()
				return image_url



	def image_urls_available(self):
		return self._image_urls is not None and len(self._image_urls) > 0
			
