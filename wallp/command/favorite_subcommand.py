
from redcmd.api import Subcommand, subcmd

from ..db import func as dbfunc, DBError


class FavoriteSubcommand(Subcommand):

	@subcmd
	def favorite(self, unfavorite=False):
		'''Favorite current wallpaper image.

		unfavorite: remove current wallpaper image from favorites'''

		try:
			if not unfavorite:
				dbfunc.favorite_wallpaper()
				print('favorited')
			else:
				dbfunc.unfavorite_wallpaper()
				print('removed from favorites')
		except DBError as e:
			print(str(e))
			raise CommandError()

