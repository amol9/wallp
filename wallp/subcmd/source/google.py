
from redcmd.api import subcmd, Arg

from .base import SourceSubcommand
from ...source.google import GoogleParams, Google


__all__ = ['GoogleSubcommand']


class GoogleSubcommand(SourceSubcommand):

	@subcmd
	def google(self, query=None, color=Arg(choices=Google.colors, default=None, opt=True)):
		'Google Images'

		gp = GoogleParams(query=query, color=color)
		self.change_wallpaper(gp)

