from random import randint

from redlib.api.misc import Retry
from redlib.http.cache2 import Cache2
from asq.initiators import query

from ..web.func import exists
from ..util import log
from .base import SourceError
from ..globals import Const
from ..util.printer import printer
from .image_filter import ImageFilter

	
class Images:

	def __init__(self, source_params, cache=False, cache_timeout=None, url_exist_check=False):
		self._list 	= []
		self._cache 	= Cache2(Const.cache_dir) if cache else None
		self._filter	= ImageFilter()

		self._source_params	= source_params
		self._cache_timeout	= 'never' if cache_timeout is None else cache_timeout
		self._url_exist_check	= url_exist_check

		self.load_cache()
		self.add_dup_filter()


	def add_dup_filter(self):
		def no_dup(image):
			return len(query(self._list).where(lambda i : i.url == image.url).to_list()) == 0

		self._filter.add_ext_filter(no_dup)


	def load_cache(self):
		if self._cache is None:
			return

		hash = self._source_params.get_hash()
		cached_images = self._cache.get(hash)
		if cached_images is not None:
			if len(cached_images) > 0:
				printer.printf('cached result', '%d images'%len(cached_images), verbosity=2)
				self._list = cached_images

	
	def add(self, image):
		if self._filter.match(image):
			self._list.append(image)


	def select(self):
		if len(self._list) == 0:
			log.error('no image urls found')
			raise SourceError('no image urls found')

		image = None
		if self._url_exist_check:
			retry = Retry(retries=10, exp_bkf=False, final_exc=SourceError('could not find usable image urls'))

			cb = printer.printf('checking', ' ', progress=True)
			while retry.left():
				image = self.select_random()
				cb.progress_cb(-1)

				if not exists(image.url):
					retry.retry()
				else:
					retry.cancel()
			cb.progress_cp()
		else:
			image =  self.select_random()

		printer.printf('random url', image.url)
		printer.printf('image title', image.title or '-', verbosity=3)
		printer.printf('username', image.user or '-', verbosity=3)
		printer.printf('image context url', image.context_url or '-', verbosity=3)

		return image


	def select_random(self):
		rindex = randint(0, len(self._list) - 1)
		image = self._list[rindex]

		del self._list[rindex]

		if self._cache is not None and self.available():
			hash = self._source_params.get_hash()
			self._cache.pickle_add(self._list, self._cache_timeout, id=hash)

		return image


	def available(self):
		return len(self._list) > 0


	def get_count(self):
		return len(self._list)


	def get_filter(self):
		return self._filter


	count = property(get_count)
	filter = property(get_filter)

