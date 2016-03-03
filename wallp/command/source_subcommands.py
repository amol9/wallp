
from redcmd.api import Subcommand, subcmd, Arg, CommandError
from redlib.api.py23 import enum_names, enum_attr

from ..client import Client, ChangeWPError
from ..util import log
from ..service.imgur import Imgur, ImgurMethod, ImageSize, ImgurParams


class SourceSubcommand(Subcommand):

	@subcmd
	def source(self):
		'Select source for wallpaper.'
		pass


class SourceSubcommands(SourceSubcommand):
	
	@subcmd
	def imgur(self, method=Arg(choices=enum_names(ImgurMethod), default=ImgurMethod.random.name),
			image_size=Arg(choices=enum_names(ImageSize), default=ImageSize.medium.name, opt=True),
			query=None, username=None, pages=1):
		'''Get new wallpaper image from imgur.com.

		method:		how to get the image for wallpaper
		query:		search query
		image_size:	preferred image size
		pages:		number of search result pages retrieved
		username:	needed when getting favorites'''

		service_params = ImgurParams(query=query, method=enum_attr(ImgurMethod, method), image_size=enum_attr(ImageSize, image_size),
				username=username, pages=int(pages))
		client = Client(service_name='imgur', service_params=service_params)

		try:
			client.change_wallpaper()
		except ChangeWPError as e:
			log.error(str(e))
			raise CommandError()

