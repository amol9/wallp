
from redcmd.api import subcmd, Arg

from .base import SourceSubcommand
from ...source.google import GoogleParams, Google


__all__ = ['GoogleSubcommand']


class GoogleSubcommand(SourceSubcommand):

	@subcmd
	def google(self, query=None, color=Arg(choices=Google.colors, default=None, opt=True), safesearch=True):
		'''Google Images

		query:		search query
		color:		preferred color
		safesearch:	turn safe search off'''

		gp = GoogleParams(query=query, color=color, safesearch=safesearch)
		self.change_wallpaper(gp)

