from random import randint

from redlib.api.misc import Retry
from redlib.http.cache2 import Cache2

from ..web.func import exists
from ..db import func as dbfunc
from ..util import log
from .base import SourceError
from ..globals import Const
from ..util.printer import printer
from ..db.app.config import Config
from ..desktop.desktop_factory import get_desktop


class Image:

	def __init__(self, url=None, title=None, description=None, user=None, context_url=None, width=None, height=None, ext=None, size=None):
		self.url		= url
		self.title		= title
		self.description	= description
		self.user		= user
		self.context_url	= context_url
		self.width		= width
		self.height		= height
		self.ext		= ext
		self.size		= size

		# to be filled in by get_image_info() by scanning the actual image data
		self.type		= None
		self.i_width		= None
		self.i_height		= None

		# temp filepath after image is downloaded
		self.temp_filepath	= None

		# filepath if an existing local image is being used
		self.filepath		= None

		# if an already used image is being reused from the db
		self.db_image		= None


class ImageFilter:

	def __init__(self, min_width=None, min_height=None, max_width=None, max_height=None, max_size=None):
		config = Config()
		
		min_ratio = config.eget('image.min_ratio_to_desktop', default=Const.min_ratio_to_desktop)
		max_ratio = config.eget('image.max_ratio_to_desktop', default=Const.max_ratio_to_desktop)

		dt = get_desktop()
		dw, dh = dt.get_size()

		self.min_width	= min_width 	or int(dw * min_ratio)
		self.min_height	= min_height 	or int(dh * min_ratio)
		self.max_width	= max_width 	or int(dw * max_ratio)
		self.max_height	= max_height 	or int(dh * max_ratio)

		self.max_size	= max_size or config.eget('image.max_size', default=Const.max_image_size)


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

		if result and image.size is not None:
			if self.max_size is not None and image.size > self.max_size:
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

		self.load_cache()


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
			retry = Retry(retries=10, exp_bkf=False)

			while retry.left():
				image = self.select_random()
				if not exists(image.url):
					retry.retry()
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

		if self._cache is not None:
			hash = self._source_params.get_hash()
			self._cache.pickle_add(self._list, self._cache_timeout, id=hash)

		return image


	def available(self):
		return len(self._list) > 0


	def get_count(self):
		return len(self._list)

	count = property(get_count)

