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


class ImgurParams(ServiceParams):
		
	def __init__(self, query=None, method=ImgurMethod.random, image_size=ImageSize.medium, pages=1, username=None):
		self.query	= query
		self.method	= method
		self.image_size	= image_size
		self.username	= username
		self.pages	= pages


class ImgurError(Exception):
	pass


ImgurMethod = Enum('ImgurMethod', ['random', 'search', 'random_album', 'wallpaper_album', 'favorite'])


@implementer(IHttpService)
class Imgur(ImageInfoMixin, ImageUrlsMixin):
	name = 'imgur'


	def __init__(self):
		super(Imgur, self).__init__()
		self._imgur = GImgur()

		dt = get_desktop()
		dw, dh = dt.get_size()
		mw, mh = 0.9 * dw, 0.9 * dh

		self.min_size = lambda w, h : w >= mw and h >= mh 


	def get_image_url(self, query=None, color=None, params=None):
		if self.image_urls_available():
			image_url = self.select_url()
			return image_url

		image_url = None
		method = None

		if params is not None and params.method != ImgurMethod.random:
			method = params.method
		elif query is not None:
			method = ImgurMethod.search
		else:
			method = choice(ImgurMethod)

		return self.map_call(query, method)


	def map_call(self, query, method):
		try:
			if method == ImgurMethod.search:
				return self.search(query)
			elif method == ImgurMethod.random_album:
				return self.random_album()
			elif method == ImgurMethod.wallpaper_album:
				return self.wallpaper_album()
			elif method == ImgurMethod.favorite:
				return self.favorite()
			else:
				raise ImgurError('invalid imgur method')
		except ImgurError as e:
			log.error(e)
			raise ServiceError()


	def random_album(self):
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

		return self.get_url_from_album(album)


	def get_url_from_album(self, album):
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

		for r in result:
			ga = lambda f : getattr(r, f, None)
			drop_ext = lambda u : u[0 : u.rfind('.')]

			if ga('link') is None or (ga('width') < mw and ga('height') < mh):
				continue

			image_context =  ImageContext(title=ga('title'), description=ga('description'), artist=ga('account_url'),url=drop_ext(ga('link')))
			self.add_url(ga('link'), image_context)

		log.debug('got %d results'%self.image_count)
		return self.select_url()


	def favorite(self, query):
		# get favorites (may be filtered)

		# add urls


	def wallpaper_albums(self, query):
		# search for: wallpaper, album

		# add results to db

		# random album

		# ad urls


