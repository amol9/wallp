
from redlib.api.misc import Retry

from ..util import log
from ..util.printer import printer
from ..db.func import get_random_favorite, FavoriteError
from .base import SourceError, SourceParams, SourceResponse
from .base_source import BaseSource


class FavoritesParams(SourceParams):
	name = 'favorites'


class Favorites(BaseSource):
	name = 'favorites'

	def get_image(self, params=None):
		return self.http_get_image_to_temp_file()


	def select_url(self):
		retry = Retry(retries=10, exp_bkf=False, final_exc=SourceError('could not find random favorite with a url'))

		while retry.left():
			try:
				image = get_random_favorite()
				if image.url is None:
					retry.retry()
					continue
				self._response.db_image = image
				return image.url

			except FavoriteError as e:
				retry.retry()
