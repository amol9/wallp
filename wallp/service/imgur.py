import re
import json
from random import choice

from zope.interface import implementer
from giraf.api import Imgur as GImgur, ImgurError as GImgurError, QueryType, ImageSize, GalleryType, ImgurErrorType

from ..util import log, Retry
from .service import IHttpService, ServiceError
from .image_info_mixin import ImageInfoMixin
from .image_urls_mixin import ImageUrlsMixin
from .image_context import ImageContext
from ..db import Config, ImgurAlbumList, SearchTermList
from ..desktop.desktop_factory import get_desktop


class ImgurError(Exception):
	pass


@implementer(IHttpService)
class Imgur(ImageInfoMixin, ImageUrlsMixin):
	name = 'imgur'


	def __init__(self):
		super(Imgur, self).__init__()
		self._imgur = GImgur()


	def get_image_url(self, query=None, color=None):
		if self.image_urls_available():
			image_url = self.select_url()
			return image_url

		image_url = None
		search = album = False

		if query is not None:
			search = True
			album = False
		else:
			search = choice([True, False])
			album = not search

		try:
			if search:
				image_url = self.get_image_url_from_search(query)
			elif album:
				image_url = self.get_image_url_from_random_album()
		except ImgurError as e:
			log.error(str(e))
			raise ServiceError(e)

		return image_url


	def get_image_url_from_search(self, query):
		self.search(query)
		image_url = self.select_url()

		log.debug('found %d urls, selected url: %s'%(self.image_count, image_url))

		return image_url


	def get_image_url_from_random_album(self):
		album_list = ImgurAlbumList()
		album = None

		retry = Retry(retries=3, final_exc=ImgurError())
		while retry.left():
			album_url = album_list.get_random()
			self.add_trace_step('selected random album', album_url)
			album_id = album_url[album_url.rfind('/') : ]

			try:
				album = self._imgur.get_album(album_id)
				retry.cancel()
			except GImgurError as e:
				log.error(e)
				if e.err_type == ImgurErrorType.not_found:
					album_list.disable(album_url)
					log.debug('disabled album: %s'%album_url)

				retry.retry()

		image_url = choice([i['link'] for i in album.images if i.get('link', None) is not None])

		self._image_context.title	= album.title
		self._image_context.description = album.description
		self._image_context.artist	= album.account_url
		self._image_context.url		= album_url

		return image_url

	
	def search(self, query):
		if query is None:
			query = SearchTermList().get_random()
			self.add_trace_step('random search term', query)

		result = self._imgur.search(query, query_type=QueryType.all, image_size=ImageSize.medium, gallery_type=GalleryType.image,
				pages=1, animated=False)

		self.add_trace_step('searched imgur', query)
		log.debug('searched for: %s'%query)

		dt = get_desktop()
		dw, dh = dt.get_size()
		mw, mh = 0.9 * dw, 0.9 * dh

		for r in result:
			ga = lambda f : getattr(r, f, None)
			drop_ext = lambda u : u[0 : u.rfind('.')]

			if ga('link') is None or (ga('width') < mw and ga('height') < mh):
				continue

			image_context =  ImageContext(title=ga('title'), description=ga('description'), artist=ga('account_url'),url=drop_ext(ga('link')))
			self.add_url(ga('link'), image_context)

