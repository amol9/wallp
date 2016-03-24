from random import randint

from ..db import func as dbfunc
from ..util import log
from .base import SourceError


class ImageUrlsMixin(object):
	def __init__(self):
		super(ImageUrlsMixin, self).__init__()
		self._image_urls 	= []
		self._image_contexts 	= {}
		#self._image_context 	= None
		self._seen_count	= 0


	def add_urls(self, image_urls):
		if len(image_urls) == 0:
			raise SourceError()
		self._image_urls += image_urls


	def add_url(self, image_url, image_context=None):
		self._image_urls.append(image_url)
		if image_context is not None:
			self._image_contexts[image_url] = image_context


	def get_image_count(self):
		return len(self._image_urls)

	image_count = property(get_image_count)


	def select_url(self, add_trace_step=True):
		if len(self._image_urls) == 0:
			log.error('no image urls found')
			raise SourceError('no image urls found')

		image_url = None

		while len(self._image_urls) > 0:
			rindex = randint(0, len(self._image_urls) - 1)
			image_url = self._image_urls[rindex]

			del self._image_urls[rindex]

			if dbfunc.image_url_seen(image_url):
				self._seen_count += 1
				continue
			else:
				if add_trace_step:
					self.add_trace_step('selected url', image_url)

				self._image_context = self._image_contexts.get(image_url, None)
				return image_url

		raise SourceError('no unseen image urls found')


	def image_urls_available(self):
		return self._image_urls is not None and ((len(self._image_urls) - self._seen_count) > 0)

