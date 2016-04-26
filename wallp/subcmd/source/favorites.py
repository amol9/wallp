
from redcmd.api import subcmd

from .base import SourceSubcommand
from ...source.favorites import FavoritesParams


__all__ = ['FavoritesSubcommand']


class FavoritesSubcommand(SourceSubcommand):

	@subcmd
	def favorites(self):
		'Favorites'

		fp = FavoritesParams()
		self.change_wallpaper(fp)

