
from redcmd.api import Subcommand, subcmd, Arg, CommandError
from redlib.api.py23 import enum_names, enum_attr

from ..client import Client, ChangeWPError
from ..util import log
from ..service.imgur import Imgur, ImgurMethod, ImageSize, ImgurParams
from ..sources.google import GoogleParams
from ..wallpaper import Wallpaper, WallpaperError


class SourceSubcommand(Subcommand):

	@subcmd
	def source(self):
		'Select source for wallpaper.'
		pass


class ImgurSubcommand(SourceSubcommand):

	@subcmd
	def imgur(self):
		'Get new wallpaper image from imgur.com.'
		pass


class ImgurSubSubcommands(ImgurSubcommand):

	# common param
	def query(self, query=None):
		'query: search query'
		self._query = query


	# common param
	def pages(self, pages=1):
		'pages: number of search result pages to retrieve'
		self._pages = int(pages)


	@subcmd
	def random(self):
		'Get wallpaper using a random method (random album / favorites / wallpaper album / search).'

		self.change_wallpaper()


	@subcmd(add=[query, pages])
	def search(self,image_size=Arg(choices=enum_names(ImageSize), default=ImageSize.medium.name, opt=True)):
		'''Search and set wallpaper from results.

		image_size:	preferred image size'''

		service_params = ImgurParams(method=ImgurMethod.search, query=self._query, image_size=enum_attr(ImageSize, image_size),
				pages=self._pages)
		self.change_wallpaper(service_params=service_params)


	@subcmd
	def random_album(self):
		'Select a random album from list.'

		service_params = ImgurParams(method=ImgurMethod.random_album)
		self.change_wallpaper(service_params=service_params)


	@subcmd(add=[query])
	def wallpaper_album(self, favorite=False):
		'''Search for wallpaper albums, add them to list, select one random album and set wallpaper from it.

		favorite: select wallpaper album from user favorites'''

		service_params = ImgurParams(method=ImgurMethod.wallpaper_album, query=self._query, favorite=favorite)
		self.change_wallpaper(service_params=service_params)

	
	@subcmd(add=[query, pages])
	def favorite(self, username=None, newest=True):
		'''Get an image from favorites of a user.

		username:	needed when getting favorites
		newest:		prefer latest favorited images'''

		service_params = ImgurParams(method=ImgurMethod.favorite, query=self._query, username=username, newest=newest, pages=self._pages)
		self.change_wallpaper(service_params=service_params)


	def change_wallpaper(self, service_params=None):
		client = Client(service_name='imgur', service_params=service_params)

		try:
			client.change_wallpaper()
		except ChangeWPError as e:
			log.error(str(e))
			raise CommandError()


class FavoritesSubcommand(SourceSubcommand):

	@subcmd
	def favorites(self):
		try:
			client = Client(service_name='favorites')
			client.change_wallpaper()
		except ChangeWPError as e:
			print(e)
			raise CommandError()


class GoogleSubcommand(SourceSubcommand):

	@subcmd
	def google(self, query=None, color=None):
		gp = GoogleParams(query=query, color=color)
		try:
			wp = Wallpaper(params=gp)
			wp.change()
		except WallpaperError as e:
			print(e)

