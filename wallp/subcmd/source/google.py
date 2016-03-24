
from redcmd.api import subcmd

from .base import SourceSubcommand
from ...source.google import GoogleParams


__all__ = ['GoogleSubcommand']


class GoogleSubcommand(SourceSubcommand):

	@subcmd
	def google(self, query=None, color=None):
		'Google Images'

		gp = GoogleParams(query=query, color=color)
		self.change_wallpaper(gp)

