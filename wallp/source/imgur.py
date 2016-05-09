import re
import json
from random import choice

from enum import Enum
from giraf.api import Imgur as GImgur, ImgurError as GImgurError, QueryType, ImageSize, GalleryType, ImgurErrorType, Filter as GImgurFilter

from ..util import log, Retry
from ..db.app.imgur_album_list import ImgurAlbumList
from ..desktop.desktop_factory import get_desktop
from ..util.printer import printer
from .base import SourceParams, SourceError, Source
from ..db.app.search_page import SearchPage, SearchPageError
from ..db.app.config import Config
from .image import Image
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from ..db.app.query_list import QueryList


ImgurMethod = Enum('ImgurMethod', ['random', 'search', 'random_album', 'wallpaper_album', 'favorite'])


class ImgurParams(SourceParams, GImgurFilter):
	name = 'imgur'
		
	def __init__(self, query=None, method=ImgurMethod.random, image_size=ImageSize.medium, pages=1, username=None, newest=False,
			favorite=False, query_type=QueryType.all, gallery_type=None, animated=False, post_id=None):

		GImgurFilter.__init__(self, query=query, image_size=image_size, pages=pages, query_type=query_type,
				gallery_type=gallery_type, animated=animated)

		self.method		= method
		self.username		= username
		self.newest		= newest
		self.favorite		= favorite
		self.post_id		= post_id

		self.hash_params = ['query', 'image_size', 'pages', 'query_type', 'gallery_type', 'animated', 'max_filesize',
				'username', 'favorite', 'start_page', 'post_id']


	def get_hash(self):
		if self.post_id is not None:
			self.hash_params = ['post_id']
		return SourceParams.get_hash(self)


class ImgurError(Exception):
	pass


class Imgur(Source):
	name = 'imgur'
	params_cls = ImgurParams

	def __init__(self):
		self._album_list = ImgurAlbumList()
		self._gimgur = None

		self._trace 	= Trace()
		self._http 	= HttpHelper()
		self._config	= Config(group=self.name)


	def get_image(self, params=None):
		self._params = params or ImgurParams()

		cache_load = self._params.method not in [ImgurMethod.random, ImgurMethod.random_album, ImgurMethod.wallpaper_album]
		self._images = Images(self._params, cache=True, cache_timeout='1h', trace=self._trace, cache_load=cache_load)

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
			raise SourceError(str(e))


	def get_gimgur(self):
		if self._gimgur is None:
			try:
				self._gimgur = GImgur()
			except GImgurError as e:
				raise SourceError(str(e))

		return self._gimgur


	def random(self):
		m = choice([self.search, self.random_album, self.wallpaper_album, self.favorite])
		return m()


	def random_album(self):
		album = None

		retry = Retry(retries=3, final_exc=ImgurError())
		while retry.left():
			album_id = self._album_list.random()
			self._trace.add_step('random album', album_id)
		
			try:
				self.get_album(album_id)
				retry.cancel()
			except ImgurError as e:
				log.error(e)
				retry.retry()


	def get_album_id_from_url(self, album_url):
		return album_url[album_url.rfind('/') : ]


	def album_images_in_cache(self, album_id):
		self._params.post_id = album_id
		self._images.load_cache()

		return self._images.available()


	def get_album(self, album_id):
		if self.album_images_in_cache(album_id):
			return

		album = None
		try:
			album = self.get_gimgur().get_album(album_id)
		except GImgurError as e:
			log.error(e)
			if e.err_type == ImgurErrorType.not_found:
				self._album_list.disable(album_id)
				log.debug('disabled album: %s'%album_id)
				raise ImgurError(e)

		self.process_album(album)


	def process_album(self, album):
		self._images.set_cache_timeout('1M')	# cache album contents for a month as they don't change much
		for i in album.images:
			image = self.make_image_obj(i, album=album)
			self._images.add(image)

	
	def search(self):
		if self._params.query is None:
			self._params.query = QueryList().random()
		else:
			self._trace.add_step('search', self._params.query)

		retry = Retry(retries=3, exp_bkf=False)

		search_page = SearchPage(group=self.name)
		page = search_page.pget(self._params.query, default=0)

		cb = printer.printf('results', '?', verbosity=2, col_updt=True)
		update_result_count = lambda c, p : cb.col_updt_cb(2, '%d (p %d)'%(c, p+1))

		while retry.left():
			self._params.start_page = page
			self._params.result.clear()

			result = self.get_gimgur().search(self._params)
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

		cb.col_updt_cp()


	def make_image_obj(self, gimage, album=None):
		if type(gimage) == GalleryType.image.value:
			get = lambda f : getattr(gimage, f, None) 
		else:
			get = lambda f : gimage.get(f, None)

		drop_ext = lambda u : u[0 : u.rfind('.')]
		image = Image()

		image.url 	= get('link')
		image.width 	= get('width')
		image.height 	= get('height')
		image.size 	= get('size')

		image.title		= get('title') or (album and album.title)
		image.description 	= get('description') or (album and album.description)
		image.user		= get('account_url') or (album and album.account_url)
		image.context_url	= (album and album.link) or drop_ext(image.url)
		
		image.nsfw = get('nsfw')
		image.score = get('score')

		return image


	def process_result(self, result, print_progress=True):
		images = []
		albums = []

		count = 0
		if print_progress:
			cb = printer.printf('results', '%d'%count, verbosity=2, col_updt=True)
			update_result_count = lambda c : cb.col_updt_cb(2, str(c))

		for r in result:
			if type(r) == GalleryType.image.value:
				image = self.make_image_obj(r)
				images.append(image)
				count += 1
			else:
				albums.append(r.id)
				count += r.images_count
			if print_progress: update_result_count(count)

		if print_progress: cb.col_updt_cp()
		log.debug('got %d results'%count)
		self.add_from_images_and_albums(images, albums)

		return count


	def add_from_images_and_albums(self, images, albums):
		def add_from_images():
			for i in images:
				self._images.add(i)

		def add_from_albums():
			album_id = choice(albums)
			albums.remove(album_id)
			self.get_album(album_id)

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

		result = self.get_gimgur().gallery_favorites(username, self._params) 

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

		def get_random_album(album_ids):
			album_id = choice(album_ids)
			self._trace.add_step('random album', album_id)
			self.get_album(album_id)

		ex_album_ids = []

		while retry.left():
			self._params.start_page = page
			result = self.get_gimgur().search(self._params)

			found_new = False
			new_album_ids = []
			for r in result:
				if not self._album_list.exists(r.id):
					self._album_list.add(r.id, commit=False)
					found_new = True
					new_album_ids.append(r.id)
					log.debug('found new wallpaper album: %s'%r.link)
				else:
					ex_album_ids.append(r.id)

			if found_new:
				self._album_list.commit()
				printer.printf('new wallpaper albums', str(len(new_album_ids)))
				get_random_album(new_album_ids)
				return
			else:
				page += 1
				retry.retry()

		if self._params.query == 'wallpaper':
			self._config.pset('wallpaper_search_page', (page + 1) % 100)

		if len(ex_album_ids) > 0:
			get_random_album(ex_album_ids)
		else:
			self.random_album()


	def get_trace(self):
		return self._trace.steps

