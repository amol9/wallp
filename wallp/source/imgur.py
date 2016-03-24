import re
import json
from random import choice

from enum import Enum
from giraf.api import Imgur as GImgur, ImgurError as GImgurError, QueryType, ImageSize, GalleryType, ImgurErrorType, Filter as GImgurFilter

from ..util import log, Retry
from .image_context import ImageContext
from ..db import ImgurAlbumList, ConfigError
from ..desktop.desktop_factory import get_desktop
from .config_mixin import ConfigMixin
from ..util.printer import printer
from .base import SourceParams, SourceError, SourceResponse
from .base_source import BaseSource
from ..db.search_page import SearchPage, SearchPageError
from ..db.config import Config


ImgurMethod = Enum('ImgurMethod', ['random', 'search', 'random_album', 'wallpaper_album', 'favorite'])


class ImgurParams(SourceParams, GImgurFilter):
	name = 'imgur'
		
	def __init__(self, query=None, method=ImgurMethod.random, image_size=ImageSize.medium, pages=1, username=None, newest=False,
			favorite=False, query_type=QueryType.all, gallery_type=None, animated=False):

		GImgurFilter.__init__(self, query=query, image_size=image_size, pages=pages, query_type=query_type,
				gallery_type=gallery_type, animated=animated, max_filesize=Config().get('image.max_size'))

		self.method		= method
		self.username		= username
		self.newest		= newest
		self.favorite		= favorite


class ImgurError(Exception):
	pass


class Imgur(BaseSource):
	name = 'imgur'

	def __init__(self):
		super(Imgur, self).__init__()
		try:
			self._imgur = GImgur()
		except GImgurError as e:
			raise SourceError(str(e))

		self._album_list = ImgurAlbumList()

		dt = get_desktop()
		dw, dh = dt.get_size()
		mw, mh = 0.9 * dw, 0.9 * dh
		self.min_size = (mw, mh)


	def get_image(self, params=None):
		if self.image_urls_available():
			return self.http_get_image_to_temp_file()

		if params is None:
			self._params = ImgurParams(query=query)
		else:
			self._params = params

		self.map_call()
		return self.http_get_image_to_temp_file()	


	def map_call(self):
		self._params.min_size = self.min_size
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
			raise SourceError()


	def random(self):
		m = choice([self.search, self.random_album, self.wallpaper_album, self.favorite])
		return m()


	def random_album(self):
		album = None

		retry = Retry(retries=3, final_exc=ImgurError())
		while retry.left():
			album_url = self._album_list.get_random()
			self.add_trace_step('random album', album_url)
		
			album = self.get_album_from_url(album_url)

			if album is not None:
				retry.cancel()
			else:
				retry.retry()

		self.process_album(album)


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
				i.get('width', None) >= self.min_size[0] and i.get('height', None) >= self.min_size[1] and\
				(self._params.max_filesize is None or i.get('size', None) <= self._params.max_filesize)

		url_list = [i['link'] for i in album.images if image_ok(i)]
		#if len(url_list) == 0:
		#	raise ImgurError('no usable image urls found')

		image_context = ImageContext(title=album.title, description=album.description, artist=album.account_url, url=album.link)
		for u in url_list:
			self.add_url(u, image_context)

	
	def search(self):
		if self._params.query is None:
			self._params.query = self.get_random_query()
		else:
			self.add_trace_step('search', self._params.query)

		retry = Retry(retries=3, exp_bkf=False)
		page = self.search_page_get(self._params.query)

		cb = printer.printf('results', '?', verbosity=2, col_cb=True)
		update_result_count = lambda c, p : cb.col_cb(2, '%d (p %d)'%(c, p+1))

		while retry.left():
			self._params.start_page = page
			self._params.result.clear()

			result = self._imgur.search(self._params)
			count = self.process_result(result, print_progress=False)
			update_result_count(count, page)

			if self.image_count > 0:
				retry.cancel()
			else:
				if self._params.result.total == 0:
					page = 0
				else:
					page += 1
				self.search_page_set(self._params.query, page)
				retry.retry()

		cb.col_update_cp()


	def process_result(self, result, print_progress=True):
		images = []
		albums = []

		count = 0
		if print_progress:
			cb = printer.printf('results', '%d'%count, verbosity=2, col_cb=True)
			update_result_count = lambda c : cb.col_cb(2, str(c))

		for r in result:
			if type(r) == GalleryType.image.value:
				ga = lambda f : getattr(r, f, None)
				drop_ext = lambda u : u[0 : u.rfind('.')]
				if ga('link') is None:
					continue

				image_context =  ImageContext(title=ga('title'), description=ga('description'),
						artist=ga('account_url'),url=drop_ext(ga('link')))
				images.append((ga('link'), image_context))
				count += 1
			else:
				albums.append(r.link)
				count += r.images_count
			if print_progress: update_result_count(count)

		if print_progress: cb.col_update_cp()
		log.debug('got %d results'%count)
		self.add_from_images_and_albums(images, albums)

		return count


	def add_from_images_and_albums(self, images, albums):
		def add_from_images():
			for i in images:
				self.add_url(i[0], i[1])

		def add_from_albums():
			album_url = choice(albums)
			albums.remove(album_url)

			album = self.get_album_from_url(album_url)
			self.process_album(album)

		add_from_images()

		while self.image_count < 1 and len(albums) > 0:
			add_from_albums()
			

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

		result = self._imgur.gallery_favorites(username, self._params) 

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
				self.config_add('wallpaper_search_page', page)
		else:
			page = 0

		retry = Retry(retries=3, delay=1, exp_bkf=False)

		while retry.left():
			self._params.start_page = page
			result = self._imgur.search(self._params)

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

				printer.printf('new wallpaper albums', str(len(album_urls)))
				self.add_trace_step('selected random album', album_url)

				album = self.get_album_from_url(album_url)
				self.process_album(album)
				return
			else:
				page += 1
				retry.retry()

		if self._params.query == 'wallpaper':
			self.config_set('wallpaper_search_page', (page + 1) % 100)
			self.random_album()


#todo: refactor, store fav wallpaper albums, add trace steps, newest
