
from redcmd.api import subcmd

from .base import SourceSubcommand
from ...source.base import SourceParams


__all__ = ['RandomSubcommand']


class RandomSubcommand(SourceSubcommand):

	@subcmd
	def random(self): 
		'Random source'

		sp = SourceParams()
		self.change_wallpaper(sp)

