from random import randint
from time import time

from redlib.api.misc import Retry
from redlib.api.http import Cache
from asq.initiators import query

from ..web.func import exists, timestamp_to_date_str
from ..util import log
from .base import SourceError
from .. import const
from ..util.printer import printer
from .image_filter import ImageFilter
from ..db.app.images import Images as DBImages
from .image_selector import ImageSelector, SelectError

	
class Images:

	def __init__(self, source_params, cache=False, cache_timeout=None, url_exist_check=False, image_alias=None,
			custom_select=None, trace=None, allow_seen_urls=False, cache_load=True):

		self._list 	= []
		self._cache 	= Cache(const.cache_dir) if (cache and const.cache_enabled) else None
		self._filter	= ImageFilter()

		self._image_alias = image_alias

		self._source_params	= source_params
		self._cache_timeout	= cache_timeout or '1M'
		self._url_exist_check	= url_exist_check

		self._allow_seen_urls = allow_seen_urls

		self._create_time = int(time())
		if cache_load:
			self.load_cache()

		self.add_filters()

		self._select_filters = []
		self._db_images = DBImages()

		self._trace = trace
		self._selector = ImageSelector(self, self._trace, custom_select=custom_select)

		self._rank = 1	# automatically added rank for images


	def add_select_filter(self, fl, retry=None, msg=None):
		self._selector.add_filter(fl, retry=retry, msg=msg)


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
		cached_data = self._cache.get(hash)
		if cached_data is not None:
			cached_images = cached_data[0]
			self._create_time = cached_data[1]

			if len(cached_images) > 0:
				item_desc = self.image_alias + 's' if len(cached_images) > 1 else ''
				info = self._cache.info(hash)
				printer.printf('cached list', '%d %s [%s]'%(len(cached_images), item_desc,
					timestamp_to_date_str(self._create_time)), verbosity=2)
				self._list = cached_images

	
	def add(self, image):
		if self._filter.match(image):
			if image.rank is None:
				image.rank = self._rank
				self._rank += 1

			self._list.append(image)


	def select(self):
		try:
			image = self._selector.select()
		except SelectError as e:
			raise SourceError(str(e))

		'''if len(self._list) == 0:
			log.error('no usable %s found'%self.image_alias)
			raise SourceError('no usable %s found'%self.image_alias)'''

		printer.printf('image title', image.title or '-', verbosity=3)
		printer.printf('username', image.user or '-', verbosity=3)
		printer.printf('image context url', image.context_url or '-', verbosity=3)

		self.update_cache()

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
		if self._cache is None:
			return

		hash = self._source_params.get_hash()

		if self.length == 0:
			self._cache.delete(hash)
			return

		self._cache.add(hash, [self._list, self._create_time], self._cache_timeout, pickle=True, updt_timeout=False)


	def available(self):
		return len(self._list) > 0


	def get_count(self):
		return len(self._list)


	def get_filter(self):
		return self._filter


	def get_image_alias(self):
		return self._image_alias or 'image'


	def set_cache_timeout(self, period):
		self._cache_timeout = period


	count 		= property(get_count)
	filter 		= property(get_filter)
	image_alias 	= property(get_image_alias)
	length		= property(get_length)

