
from redcmd.api import subcmd

from .base import SourceSubcommand
from ...source.bitmap import BitmapParams


__all__ = ['ColorSubcommand']


class ColorSubcommand(SourceSubcommand):

	@subcmd
	def color(self, color=None):
		'''Solid color

		run "wallp list colors" to see a list of all supported colors'''

		bp = BitmapParams(color=color)
		self.change_wallpaper(bp)

