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
from ..db.app.images import Images as DBImages

	
class Images:

	def __init__(self, source_params, cache=False, cache_timeout=None, url_exist_check=False, image_alias=None, selector=None, trace=None):
		self._list 	= []
		self._cache 	= Cache2(Const.cache_dir) if cache else None
		self._filter	= ImageFilter()

		self._image_alias = image_alias

		self._source_params	= source_params
		self._cache_timeout	= 'never' if cache_timeout is None else cache_timeout
		self._url_exist_check	= url_exist_check

		self.load_cache()
		self.add_filters()

		self._select_filters = []
		self._db_images = DBImages()

		self._selector = selector or self.select_random
		self._trace = trace


	def add_select_filter(self, fn):
		self._select_filters.append(fn)


	def add_filters(self):
		def no_dup(image, list):
			return image.url is None or len(query(list).where(lambda i : i.url == image.url).to_list()) == 0

		self.add_list_filter(no_dup)

		def url_not_seen(image, db_images):
			return image.url is None or not db_images.seen_by_url(image.url)

		self.add_db_filter(url_not_seen)


	def add_list_filter(self, fn):
		self._filter.add_ext_filter(lambda i : fn(i, self._list))


	def add_db_filter(self, fn):
		self._filter.add_ext_filter(lambda i : fn(i, self._db_images))


	def load_cache(self):
		if self._cache is None:
			return

		hash = self._source_params.get_hash()
		cached_images = self._cache.get(hash)
		if cached_images is not None:
			if len(cached_images) > 0:
				item_desc = self.image_alias + 's' if len(cached_images) > 1 else ''
				printer.printf('cached', '%d %s'%(len(cached_images), item_desc), verbosity=2)
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
				image = self._selector()
				cb.progress_cb(-1)

				if not exists(image.url):
					retry.retry()
				else:
					retry.cancel()
			cb.progress_cp()

		elif len(self._select_filters) > 0:
			image = self._selector()
			map(lambda f : f(image), self._select_filters)
		else:
			image = self._selector()

		printer.printf('image title', image.title or '-', verbosity=3)
		printer.printf('username', image.user or '-', verbosity=3)
		printer.printf('image context url', image.context_url or '-', verbosity=3)

		self.update_cache()

		return image


	def select_random(self):
		rindex = randint(0, len(self._list) - 1)
		image = self._list[rindex]
		self._trace.add_step('random %s'%self.image_alias, image.url or image.context_url, overwrite=True)

		del self._list[rindex]
		return image


	def update_cache(self):
		if self._cache is not None and self.available():
			hash = self._source_params.get_hash()
			self._cache.pickle_add(self._list, self._cache_timeout, id=hash)


	def available(self):
		return len(self._list) > 0


	def get_count(self):
		return len(self._list)


	def get_filter(self):
		return self._filter


	def get_image_alias(self):
		return self._image_alias or 'image'


	count 		= property(get_count)
	filter 		= property(get_filter)
	image_alias 	= property(get_image_alias)

