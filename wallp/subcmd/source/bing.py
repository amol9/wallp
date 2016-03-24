
from redcmd.api import subcmd

from .base import SourceSubcommand
from ...source.bing import BingParams


__all__ = ['BingSubcommand']


class BingSubcommand(SourceSubcommand):

	@subcmd
	def bing(self):
		'Bing Gallery'

		bp = BingParams()
		self.change_wallpaper(bp)

