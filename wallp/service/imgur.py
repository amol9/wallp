import re
import json
from random import choice

from enum import Enum
from zope.interface import implementer
from giraf.api import Imgur as GImgur, ImgurError as GImgurError, QueryType, ImageSize, GalleryType, ImgurErrorType

from ..util import log, Retry
from .service import IHttpService, ServiceError
from .image_info_mixin import ImageInfoMixin
from .image_urls_mixin import ImageUrlsMixin
from .image_context import ImageContext
from ..db import Config, ImgurAlbumList, SearchTermList, ConfigError, NotFoundError
from ..desktop.desktop_factory import get_desktop
from .service_params import ServiceParams


ImgurMethod = Enum('ImgurMethod', ['random', 'search', 'random_album', 'wallpaper_album', 'favorite'])


class ImgurParams(ServiceParams):
		
	def __init__(self, query=None, method=ImgurMethod.random, image_size=ImageSize.medium, pages=1, username=None):
		self.query	= query
		self.method	= method
		self.image_size	= image_size
		self.username	= username
		self.pages	= pages


class ImgurError(Exception):
	pass


@implementer(IHttpService)
class Imgur(ImageInfoMixin, ImageUrlsMixin):
	name = 'imgur'


	def __init__(self):
		super(Imgur, self).__init__()
		self._imgur = GImgur()

		dt = get_desktop()
		dw, dh = dt.get_size()
		mw, mh = 0.9 * dw, 0.9 * dh
		self.min_size = (mw, mh)


	def get_image_url(self, query=None, color=None, params=None):
		if self.image_urls_available():
			image_url = self.select_url()
			return image_url

		if params is None:
			self._params = ImgurParams(query=query)
		else:
			self._params = params

		if query is not None:
			self._params.method = ImgurMethod.search

		return self.map_call()


	def map_call(self):
		method = self._params.method
		try:
			if method == ImgurMethod.search:
				return self.search()
			elif method == ImgurMethod.random_album:
				return self.random_album()
			elif method == ImgurMethod.wallpaper_album:
				return self.wallpaper_album()
			elif method == ImgurMethod.favorite:
				return self.favorite()
			else:
				return self.random()
		except ImgurError as e:
			log.error(e)
			raise ServiceError()


	def random(self):
		m = choice([self.search, self.random_album, self.wallpaper_album, self.favorite])
		return m()


	def random_album(self):
		album_list = ImgurAlbumList()
		album = None

		retry = Retry(retries=3, final_exc=ImgurError())
		while retry.left():
			album_url = album_list.get_random()
			self.add_trace_step('selected random album', album_url)
		
			album = self.get_album_from_url(album_url)

			if album is not None:
				retry.cancel()
			else:
				retry.retry()

		return self.get_url_from_album(album)


	def get_album_from_url(self, album_url):
		album_id = album_url[album_url.rfind('/') : ]
		album = None

		try:
			album = self._imgur.get_album(album_id)
		except GImgurError as e:
			log.error(e)
			if e.err_type == ImgurErrorType.not_found:
				album_list.disable(album_url)
				log.debug('disabled album: %s'%album_url)

		return album


	def get_url_from_album(self, album):
		image_ok = lambda i : i.get('link', None) is not None and\
				i.get('width', None) >= self.min_size[0] and i.get('height', None) >= self.min_size[1]

		url_list = [i['link'] for i in album.images if image_ok(i)]
		if len(url_list) == 0:
			raise ImgurError('no usable image urls found')

		image_url = choice(url_list)

		self._image_context.title	= album.title
		self._image_context.description = album.description
		self._image_context.artist	= album.account_url
		self._image_context.url		= album.link

		return image_url

	
	def search(self):
		query = self._params.query
		if query is None:
			query = SearchTermList().get_random()
			self.add_trace_step('random search term', query)

		result = self._imgur.search(query, query_type=QueryType.all, image_size=ImageSize.medium, gallery_type=GalleryType.image,
				pages=self._params.pages, animated=False, min_size=self.min_size)

		self.add_trace_step('searched imgur', query)

		self.process_result(result)
		return self.select_url()


	def process_result(self, result):
		for r in result:
			ga = lambda f : getattr(r, f, None)
			drop_ext = lambda u : u[0 : u.rfind('.')]

			if ga('link') is None:
				continue

			image_context =  ImageContext(title=ga('title'), description=ga('description'), artist=ga('account_url'),url=drop_ext(ga('link')))
			self.add_url(ga('link'), image_context)

		log.debug('got %d results'%self.image_count)


	def favorite(self):
		result = self._imgur.gallery_favorites(self._params.username, query=self._params.query, query_type=QueryType.all,
				gallery_type=GalleryType.image, pages=self._params.pages, animated=False, min_size=self.min_size)

		self.process_result(result)
		return self.select_url()



	def wallpaper_album(self):
		config = Config()
		page = None

		try:
			page = config.get('imgur.wallpaper_search_page')
		except (NotFoundError, ConfigError):
			page = 0
			config.add('imgur.wallpaper_search_page', page, int)
			config.commit()

		retry = Retry(retries=3, delay=1, exp_bkf=False)

		while retry.left():
			result = self._imgur.search('wallpaper', query_type=QueryType.all, gallery_type=GalleryType.album, start_page=page)
			album_list = ImgurAlbumList()

			found_new = False
			album_urls = []
			for r in result:
				if not album_list.exists(r.link):
					album_list.add(r.link, True)
					found_new = True
					album_urls.append(r.link)
					log.debug('found new wallpaper album: %s'%r.link)

			if found_new:
				album_list.commit()
				album = self.get_album_from_url(choice(album_urls))
				return self.get_url_from_album(album)
			else:
				page += 1
				retry.retry()

		config.set('imgur.wallpaper_search_page', (page + 1) % 100)
		config.commit()
		return self.random_album()

