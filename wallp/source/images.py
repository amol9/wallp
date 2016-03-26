from random import randint

from redlib.api.misc import Retry
from redlib.http.cache2 import Cache2

from ..web.func import exists
from ..db import func as dbfunc
from ..util import log
from .base import SourceError
from ..globals import Const


class Image:

	def __init__(self, url=None, title=None, description=None, user=None, context_url=None, width=None, height=None, ext=None):
		self.url		= url
		self.title		= title
		self.description	= description
		self.user		= user
		self.context_url	= context_url
		self.width		= width
		self.height		= height
		self.ext		= ext

		# to be filled in by get_image_info() by scanning the actual image data
		self.type		= None
		self.i_width		= None
		self.i_height		= None

		# temp filepath after image is downloaded
		self.temp_filepath	= None


class ImageFilter:

	def __init__(self, min_width=None, min_height=None, max_width=None, max_height=None):
		self.min_width	= min_width
		self.min_height	= min_height
		self.max_width	= max_width
		self.max_height	= max_height

		self.url_exist_check	= url_exist_check


	def match(self, image):
		result = True

		if dbfunc.image_url_seen(image.url):
			result = False

		if result and image.width is not None:
			if self.min_width is not None and image.width < self.min_width:
				result = False
			if result and self.max_width is not None and image.width > self.max_width:
				result = False

		if result and image.height is not None:
			if self.min_height is not None and image.height < self.min_height:
				result = False
			if result and self.max_height is not None and image.height > self.max_height:
				result = False

		return result

	
class Images:

	def __init__(self, source_params, cache=False, cache_timeout=None, url_exist_check=False):
		self._list 	= []
		self._cache 	= Cache2(Const.cache_dir) if cache else None
		self._filter	= ImageFilter()

		self._source_params	= source_params
		self._cache_timeout	= 'never' if cache_timeout is None else cache_timeout
		self._url_exist_check	= url_exist_check


	def load_cache(self):
		cached_images = self._cache.get(self._source_params.hash())

		if cached_images is not None:
			if len(cached_images) > 0:
				self._list = cached_images

	
	def add_image(self, image):
		if self._filter.match(image):
			self._list.append(image)


	def select(self):
		if len(self._list) == 0:
			log.error('no image urls found')
			raise SourceError('no image urls found')

		image_url = None
		if self._url_exist_check:
			retry = Retry(retries=10, exp_bkf=False)

			while retry.left():
				image_url = self.select_random()
				if not exists(image.url):
					retry.retry()
		else:
			image_url =  self.select_random()


		return image_url


	def select_random(self):
		rindex = randint(0, len(self._list) - 1)
		image = self._list[rindex]

		del self._list[rindex]

		if self._cache is not None:
			self._cache.pickle_add((self._list, self._cache_timeout, id=self._source_params.hash())

		return image


	def available(self):
		return len(self._list) > 0


	def get_image_count(self):
		return len(self._list)

	image_count = property(get_image_count)

