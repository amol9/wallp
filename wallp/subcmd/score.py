
from redcmd.api import Subcommand, subcmd, CommandError

from ..db.app.images import Images, DBImageError


__all__ = ['ScoreSubcommands']


class ScoreSubcommands(Subcommand):

	def __init__(self):
		self._db_images = Images()


	@subcmd
	def like(self):
		self.exc_call(self._db_images.like_wallpaper)
		

	@subcmd
	def dislike(self):
		self.exc_call(self._db_images.dislike_wallpaper)


	def exc_call(self, method):
		try:
			score = method()
			print('image score: %d'%score)
		except DBImageError as e:
			print(str(e))
			raise CommandError()

