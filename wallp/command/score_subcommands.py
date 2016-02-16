
from redcmd.api import Subcommand, subcmd

from ..db import func as dbfunc


class ScoreSubcommands(Subcommand):

	@subcmd
	def like(self):
		self.score_call(dbfunc.like_wallpaper)
		

	@subcmd
	def dislike(self):
		self.score_call(dbfunc.dislike_wallpaper)


	def score_call(self, func):
		try:
			score = func()
			print('image score: %d'%score)
		except LikeError as e:
			print(str(e))
			raise CommandError()

