
from redcmd.api import subcmd

from .base import ConfigSubcommand


class ListSubcommand(ConfigSubcommand):

	@subcmd
	def list(self):
		pass


class ListOps:

	@subcmd
	def add(self, item):
		pass

	@subcmd
	def remove(self, item):
		pass

	@subcmd
	def enable(self, item):
		pass

	@subcmd
	def disable(self, item):
		pass

	@subcmd
	def dump(self):
		pass


class ImgurAlbumSubcommand(ListSubcommand):

	@subcmd
	def imgur_album(self):
		pass


class ImgurAlbumOps(ImgurAlbumSubcommand, ListOps):
	pass


	#imgur-album add/..
	#query ..
	#subreddit ..

