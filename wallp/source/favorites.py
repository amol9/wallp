
from ..util import log
from .base import SourceError, SourceParams, Source
from .image import Image
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from ..db.app.images import Images as DBImages, DBImageError


class FavoritesParams(SourceParams):
	name = 'favorites'


class Favorites(Source):
	name = 'favorites'
	params_cls = FavoritesParams

	def __init__(self):
		self._trace 	= Trace()
		self._http 	= HttpHelper()
		self._db_images	= DBImages()


	def get_image(self, params=None):
		params = params or FavoritesParams()

		self._images = Images(params, cache=False, trace=self._trace, allow_seen_urls=True, custom_select=self.select_random_favorite)
		self._images.filter.allow_seen_images = True

		return self._http.download_image(self._images, self._trace)


	def select_random_favorite(self):
		image = Image()
		try:
			image.init_from_db_image(self._db_images.random_favorite())
		except DBImageError as e:
			raise SourceError(str(e))

		return image

	
	def get_trace(self):
		return self._trace.steps

