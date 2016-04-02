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
from .image_selector import ImageSelector

	
class Images:

	def __init__(self, source_params, cache=False, cache_timeout=None, url_exist_check=False, image_alias=None,
			selector=None, trace=None, allow_seen_urls=False, cache_load=True):
		self._list 	= []
		self._cache 	= Cache2(Const.cache_dir) if cache else None
		self._filter	= ImageFilter()

		self._image_alias = image_alias

		self._source_params	= source_params
		self._cache_timeout	= 'never' if cache_timeout is None else cache_timeout
		self._url_exist_check	= url_exist_check

		self._allow_seen_urls = allow_seen_urls

		if cache_load:
			self.load_cache()
		self.add_filters()

		self._select_filters = []
		self._db_images = DBImages()

		self._trace = trace
		self._selector = selector or ImageSelector(self, self._trace)

		self._rank = 1	# automatically added rank for images


	def add_select_filter(self, fn):
		self._select_filters.append(fn)


	def add_filters(self):
		def no_dup(image, list):
			return image.url is None or len(query(list).where(lambda i : i.url == image.url).to_list()) == 0

		self.add_list_filter(no_dup)

		if not self._allow_seen_urls:
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
				printer.printf('cached list', '%d %s'%(len(cached_images), item_desc), verbosity=2)
				self._list = cached_images

	
	def add(self, image):
		if self._filter.match(image):
			if image.rank is None:
				image.rank = self._rank
				self._rank += 1

			self._list.append(image)


	def select(self):
		return self._selector.select()

		if len(self._list) == 0:
			log.error('no usable %s found'%self.image_alias)
			raise SourceError('no usable %s found'%self.image_alias)

		image = None
		if self._url_exist_check:
			retry = Retry(retries=10, exp_bkf=False, final_exc=SourceError('could not find usable image urls'))

			cb = printer.printf('checking', ' ', progress=True)
			while retry.left():
				image = self._selector(print_step=False)
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


	def select_random(self, print_step=True):
		rindex = randint(0, len(self._list) - 1)
		image = self._list[rindex]

		self._trace.add_step('random %s'%self.image_alias, image.url or image.context_url, overwrite=True, print_step=print_step)

		del self._list[rindex]
		return image


	def get_length(self):
		return len(self._list)


	def get_image(self, index=None, fn=None):
		if len(self._list) == 0:
			raise SourceError('no usable %s found'%self.image_alias)

		if index is not None:
			return self._list[index]
		elif fn is not None:
			return fn(self._list)


	def del_image(self, index=None, image=None):
		if index is not None:
			del self._list[index]
		elif image is not None:
			self._list.remove(image)

		self.update_cache()


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
	length		= property(get_length)

