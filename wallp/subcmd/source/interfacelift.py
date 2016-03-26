
from redcmd.api import subcmd, IntArg

from .base import SourceSubcommand
from ...source.interfacelift import InterfaceliftParams


__all__ = ['InterfaceliftSubcommand']


class InterfaceliftSubcommand(SourceSubcommand):

	@subcmd
	def interfacelift(self, page=IntArg(min=1, opt=True)):
		'interfacelift.com'

		ip = InterfaceliftParams(page=page)
		self.change_wallpaper(ip)

