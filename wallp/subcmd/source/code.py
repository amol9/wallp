
from redcmd.api import subcmd, Arg

from .base import SourceSubcommand
from ...source.code import CodeParams


__all__ = ['CodeSubcommand']


class CodeSubcommand(SourceSubcommand):

	@subcmd
	def code(self, filepath, font_name=None, font_size=14):
		'''Source code

		filepath:	path to source code file
		font_name:	font name
		font_size:	font size'''

		cp = CodeParams(filepath, font_name=font_name, font_size=font_size)
		self.change_wallpaper(cp)

