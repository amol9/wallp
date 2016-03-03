
from redcmd.api import Subcommand, subcmd, Arg, CommandError
from redlib.api.py23 import enum_names, enum_attr

from ..client import Client, ChangeWPError
from ..util import log
from ..service.imgur import Imgur, ImgurMethod, ImageSize


class SourceSubcommands(Subcommand):
	
	@subcmd
	def imgur(self, method=Arg(choice=enum_names(ImgurMethod), default=ImgurMethod.random.name),
			image_size=Arg(choice=enum_names(ImageSize), default=ImageSize.medium, opt=True),
			query=None, username=None, pages=1):
		'''Get new wallpaper image from imgur.com.

		method:		how to get the image for wallpaper
		query:		search query
		image_size:	preferred image size
		pages:		number of search result pages retrieved
		username:	needed when getting favorites'''

		service_params = ImgurParams(method=enum_attr(ImgurMethod, method), image_size=enum_attr(ImageSize, image_size),
				query=query, username=username, pages=pages)
		client = Client(service_name='imgur', query=query, service_params=service_params)

		try:
			client.change_wallpaper()
		except ChangeWPError as e:
			log.error(str(e))
			raise CommandError()

