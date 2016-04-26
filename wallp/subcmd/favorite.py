
from redcmd.api import Subcommand, subcmd, CommandError

from ..db.app.images import Images, DBImageError


__all__ = ['FavoriteSubcommand']


class FavoriteSubcommand(Subcommand):

	@subcmd
	def favorite(self, unfavorite=False):
		'''Favorite current wallpaper image.
		unfavorite: remove current wallpaper image from favorites'''

		db_images = Images()
		try:
			if not unfavorite:
				db_images.favorite_wallpaper()
				print('favorited')
			else:
				db_images.unfavorite_wallpaper()
				print('removed from favorites')
		except DBImageError as e:
			print(str(e))
			raise CommandError()

