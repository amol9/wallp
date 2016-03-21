
from redcmd.api import Subcommand, subcmd, CommandError

from ..db.func import favorite_wallpaper, unfavorite_wallpaper, FavoriteError
from ..db import DBError


class FavoriteSubcommand(Subcommand):

	@subcmd
	def favorite(self, unfavorite=False):
		'''Favorite current wallpaper image.

		unfavorite: remove current wallpaper image from favorites'''

		try:
			if not unfavorite:
				favorite_wallpaper()
				print('favorited')
			else:
				unfavorite_wallpaper()
				print('removed from favorites')
		except (DBError, FavoriteError) as e:
			print(str(e))
			raise CommandError()

