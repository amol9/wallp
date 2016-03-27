
from ..util import log
from ..db.func import get_random_favorite, FavoriteError
from .base import SourceError, SourceParams, Source
from .image import Image
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace


class FavoritesParams(SourceParams):
	name = 'favorites'


class Favorites(Source):
	name = 'favorites'

	def __init__(self):
		self._trace 	= Trace()
		self._http 	= HttpHelper()


	def get_image(self, params=None):
		params = params or FavoritesParams()

		self._images = Images(params, cache=False)
		self._images.filter.allow_seen_images = True

		self.select_set()
		return self._http.download_image(self._images, self._trace)


	def select_set(self):
		for _ in range(0, 20):
			try:
				db_image = get_random_favorite()
				if db_image.url is None:
					continue

				image = Image()
				image.init_from_db_image(db_image)

				self._images.add(image)

			except FavoriteError as e:
				raise SourceError('no favorites found')
