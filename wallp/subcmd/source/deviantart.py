
from redcmd.api import subcmd

from .base import SourceSubcommand
from ...source.deviantart import DeviantArtParams


__all__ = ['DeviantArtSubcommand']


class DeviantArtSubcommand(SourceSubcommand):

	@subcmd
	def deviantart(self, query=None):
		'deviantart.com'

		dp = DeviantArtParams(query=query)
		self.change_wallpaper(dp)

