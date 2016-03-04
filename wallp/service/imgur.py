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
from ..db import ImgurAlbumList, SearchTermList, ConfigError
from ..desktop.desktop_factory import get_desktop
from .service_params import ServiceParams
from .config_mixin import ConfigMixin


ImgurMethod = Enum('ImgurMethod', ['random', 'search', 'random_album', 'wallpaper_album', 'favorite'])


class ImgurParams(ServiceParams):
		
	def __init__(self, query=None, method=ImgurMethod.random, image_size=ImageSize.medium, pages=1, username=None, newest=False,
			favorite=False, query_type=QueryType.all, gallery_type=None):
		self.query		= query
		self.method		= method
		self.image_size		= image_size
		self.username		= username
		self.pages		= pages
		self.newest		= newest
		self.favorite		= favorite
		self.query_type		= query_type
		self.gallery_type	= gallery_type


class ImgurError(Exception):
	pass


@implementer(IHttpService)
class Imgur(ImageInfoMixin, ImageUrlsMixin, ConfigMixin):
	name = 'imgur'

	def __init__(self):
		super(Imgur, self).__init__()
		self._imgur = GImgur()
		self._album_list = ImgurAlbumList()

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
		album = None

		retry = Retry(retries=3, final_exc=ImgurError())
		while retry.left():
			album_url = self._album_list.get_random()
			self.add_trace_step('selected random album', album_url)
		
			album = self.get_album_from_url(album_url)

			if album is not None:
				retry.cancel()
			else:
				retry.retry()

		self.process_album(album)
		return self.select_url()


	def get_album_from_url(self, album_url):
		album_id = album_url[album_url.rfind('/') : ]
		album = None

		try:
			album = self._imgur.get_album(album_id)
		except GImgurError as e:
			log.error(e)
			if e.err_type == ImgurErrorType.not_found:
				self._album_list.disable(album_url)
				log.debug('disabled album: %s'%album_url)

		return album


	def process_album(self, album):
		image_ok = lambda i : i.get('link', None) is not None and\
				i.get('width', None) >= self.min_size[0] and i.get('height', None) >= self.min_size[1]

		url_list = [i['link'] for i in album.images if image_ok(i)]
		if len(url_list) == 0:
			raise ImgurError('no usable image urls found')

		image_context = ImageContext(title=album.title, description=album.description, artist=album.account_url, url=album.link)
		for u in url_list:
			self.add_url(u, image_context)

	
	def search(self):
		query = self._params.query
		if query is None:
			query = SearchTermList().get_random()
			self.add_trace_step('random search term', query)

		result = self._imgur.search(query, query_type=QueryType.all, image_size=ImageSize.medium, gallery_type=GalleryType.image,
				pages=self._params.pages, animated=False, min_size=self.min_size)

		self.add_trace_step('searched imgur', query)

		return self.process_result(result)


	def process_result(self, result):
		images = []
		albums = []

		for r in result:
			if type(r) == GalleryType.image.value:
				ga = lambda f : getattr(r, f, None)
				drop_ext = lambda u : u[0 : u.rfind('.')]
				if ga('link') is None:
					continue

				image_context =  ImageContext(title=ga('title'), description=ga('description'),
						artist=ga('account_url'),url=drop_ext(ga('link')))
				images.append((ga('link'), image_context))
			else:
				albums.append(r.link)

		log.debug('got %d results'%(len(images) + len(albums)))

		def choose_from_images():
			for i in images:
				self.add_url(i[0], i[1])

		def choose_from_albums():
			album_url = choice(albums)
			album = self.get_album_from_url(album_url)
			self.process_album(album)

		if len(images) > 0 and len(albums) > 0:
			ch = choice([True, False])
			if ch:
				choose_from_images()
			else:
				choose_from_albums()
		elif len(images) > 0:
			choose_from_images()
		elif len(albums) > 0:
			choose_from_albums()
		else:
			raise ImgurError('no images found')

		return self.select_url()
		

	def favorite(self):
		username = self._params.username
		if username is None:
			try:
				username = self.config_get('username')
			except ConfigError as e:
				log.error(e)
				raise ImgurError('cannot get favorite without username')
		else:
			self.config_set('username', username)

		result = self._imgur.gallery_favorites(username, query=self._params.query, query_type=self._params.query_type,
				gallery_type=self._params.gallery_type, pages=self._params.pages, animated=False, min_size=self.min_size)

		return self.process_result(result)


	def wallpaper_album(self):
		if self._params.query is not None:
			self._params.query += ' wallpaper'
		else:
			self._params.query = 'wallpaper'

		self._params.query_type = QueryType.all
		self._params.gallery_type = GalleryType.album

		if self._params.favorite:
			return self.wallpaper_album_from_favorites()
		else:
			return self.wallpaper_album_from_search()


	def wallpaper_album_from_favorites(self):
		return self.favorite()


	def wallpaper_album_from_search(self):
		page = None

		if self._params.query == 'wallpaper':
			try:
				page = self.config_get('wallpaper_search_page')
			except ConfigError:
				page = 0
				self.config_add('wallpaper_search_page', page, int)
		else:
			page = 0

		retry = Retry(retries=3, delay=1, exp_bkf=False)

		while retry.left():
			result = self._imgur.search(self._params.query, query_type=self._params.query_type,
					gallery_type=self._params.gallery_type, start_page=page)

			found_new = False
			album_urls = []
			for r in result:
				if not self._album_list.exists(r.link):
					self._album_list.add(r.link, True)
					found_new = True
					album_urls.append(r.link)
					log.debug('found new wallpaper album: %s'%r.link)

			if found_new:
				self._album_list.commit()
				album_url = choice(album_urls)
				self.add_trace_step('selected random album', album_url)
				album = self.get_album_from_url(album_url)
				self.process_album(album)
				return self.select_url()
			else:
				page += 1
				retry.retry()

		if self._params.query == 'wallpaper':
			self.config_set('wallpaper_search_page', (page + 1) % 100)
		return self.random_album()

#todo: refactor, store fav wallpaper albums, add trace steps
