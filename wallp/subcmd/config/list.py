
from redcmd.api import subcmd

from .base import ConfigSubcommand


class ListSubcommand(ConfigSubcommand):

	@subcmd
	def list(self):
		pass


class ListOps:

	@subcmd
	def add(self, item):
		'Add to list.'
		pass

	@subcmd
	def remove(self, item):
		'Remove from list.'
		pass

	@subcmd
	def enable(self, item):
		'Enable an item.'
		pass

	@subcmd
	def disable(self, item):
		'Disable an item.'
		pass

	@subcmd
	def dump(self):
		'Print entire list.'
		pass


class ImgurAlbumSubcommand(ListSubcommand):

	@subcmd
	def imgur_album(self):
		pass


class ImgurAlbumOps(ImgurAlbumSubcommand, ListOps):
	pass

