
from zope.interface import implementer

from ..util import log
from .service import IHttpService, ServiceError
from ..util.printer import printer
from ..db.func import get_random_favorite, FavoriteError


@implementer(IHttpService)
class Favorites:
	name = 'favorites'

	def __init__(self):
		self.saved_image = None


	def get_image_url(self, **kwargs):
		try:
			image = get_random_favorite()
			self.saved_image = image
		except FavoriteError as e:
			raise ServiceError(str(e))

