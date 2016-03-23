
from .base import SourceSubcommand
from ...source.favorites import FavoritesParams


__all__ = ['FavoritesSubcommand']


class FavoritesSubcommand(SourceSubcommand):

	@subcmd
	def favorites(self):
		fp = FavoritesParams()
		self.change_wallpaper(fp)

