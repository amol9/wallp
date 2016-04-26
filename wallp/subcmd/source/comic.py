
from redcmd.api import subcmd, Arg

from .base import SourceSubcommand
from ...source.comic.xkcd import XkcdParams


__all__ = ['ComicSubcommand']


class ComicSubcommand(SourceSubcommand):

	@subcmd(add_skip=True)
	def comic(self):
		'Comic strip sources'
		pass


class ComicSubSubcommands(ComicSubcommand):

	@subcmd
	def xkcd(self, latest=False):
		'xkcd.com'

		xp = XkcdParams(latest=latest)
		self.change_wallpaper(xp)

