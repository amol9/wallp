import re
import json
from random import choice

from enum import Enum
from giraf.api import Imgur as GImgur, ImgurError as GImgurError, QueryType, ImageSize, GalleryType, ImgurErrorType, Filter as GImgurFilter

from ..util import log, Retry
from ..db import ImgurAlbumList
from ..desktop.desktop_factory import get_desktop
from ..util.printer import printer
from .base import SourceParams, SourceError, Source
from ..db.app.search_page import SearchPage, SearchPageError
from ..db.app.config import Config
from .image import Image
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from ..db import SearchTermList


ImgurMethod = Enum('ImgurMethod', ['random', 'search', 'random_album', 'wallpaper_album', 'favorite'])


class ImgurParams(SourceParams, GImgurFilter):
	name = 'imgur'
		
	def __init__(self, query=None, method=ImgurMethod.random, image_size=ImageSize.medium, pages=1, username=None, newest=False,
			favorite=False, query_type=QueryType.all, gallery_type=None, animated=False):

		GImgurFilter.__init__(self, query=query, image_size=image_size, pages=pages, query_type=query_type,
				gallery_type=gallery_type, animated=animated)

		self.method		= method
		self.username		= username
		self.newest		= newest
		self.favorite		= favorite

		self.hash_params = ['query', 'image_size', 'pages', 'query_type', 'gallery_type', 'animated', 'max_filesize',
				'method', 'username', 'favorite', 'start_page']


class ImgurError(Exception):
	pass


class Imgur(Source):
	name = 'imgur'
	params_cls = ImgurParams

	def __init__(self):
		try:
			self._imgur = GImgur()
		except GImgurError as e:
			raise SourceError(str(e))

		self._album_list = ImgurAlbumList()

		self._trace 	= Trace()
		self._http 	= HttpHelper()
		self._config	= Config(group=self.name)


	def get_image(self, params=None):
		self._params = params or ImgurParams()
		self._images = Images(self._params, cache=True, trace=self._trace)

		if not self._images.available():
			self.map_call()

		return self._http.download_image(self._images, self._trace)


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
			raise SourceError()


	def random(self):
		m = choice([self.search, self.random_album, self.wallpaper_album, self.favorite])
		return m()


	def random_album(self):
		album = None

		retry = Retry(retries=3, final_exc=ImgurError())
		while retry.left():
			album_url = self._album_list.get_random()
			self._trace.add_step('random album', album_url)
		
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
		for i in album.images:
			image = Image()

			image.url 	= i.get('link')
			image.width 	= i.get('width')
			image.height 	= i.get('height')
			image.size 	= i.get('size')
		
			image.title		= i.get('title') or album.title
			image.description 	= i.get('description') or album.description
			image.user		= i.get('account_url')
			image.context_url	= album.link
			
			#image.nsfw = i.get('nsfw')
			#image.score = i.get('score')

			self._images.add(image)

	
	def search(self):
		if self._params.query is None:
			self._params.query = SearchTermList().get_random()
		else:
			self._trace.add_step('search', self._params.query)

		retry = Retry(retries=3, exp_bkf=False)

		search_page = SearchPage(group=self.name)
		page = search_page.pget(self._params.query, default=0)

		cb = printer.printf('results', '?', verbosity=2, col_cb=True)
		update_result_count = lambda c, p : cb.col_cb(2, '%d (p %d)'%(c, p+1))

		while retry.left():
			self._params.start_page = page
			self._params.result.clear()

			result = self._imgur.search(self._params)
			count = self.process_result(result, print_progress=False)
			update_result_count(count, page)

			if self._images.available():
				retry.cancel()
			else:
				if self._params.result.total == 0:
					page = 0
				else:
					page += 1
				search_page.pset(self._params.query, page)
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

				image = Image(url=ga('link'), title=ga('title'), description=ga('description'), user=ga('account_url'),
						context_url=drop_ext(ga('link')), width=ga('width'), height=ga('height'), size=ga('size'))
				images.append(image)
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
				self._images.add(i)

		def add_from_albums():
			album_url = choice(albums)
			albums.remove(album_url)

			album = self.get_album_from_url(album_url)
			self.process_album(album)

		add_from_images()

		while not self._images.available() and len(albums) > 0:
			add_from_albums()
			

	def favorite(self):
		username = self._params.username

		if username is None:
			username = self._config.pget('username', default=None)
			if username is None:
				raise ImgurError('cannot get favorite without username')
		else:
			self._config.pset('username', username)

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
			page = self._config.pget('wallpaper_search_page', default=0)
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
				self._trace.add_step('selected random album', album_url)

				album = self.get_album_from_url(album_url)
				self.process_album(album)
				return
			else:
				page += 1
				retry.retry()

		if self._params.query == 'wallpaper':
			self._config.pset('wallpaper_search_page', (page + 1) % 100)
			self.random_album()


	def get_trace(self):
		return self._trace.steps

