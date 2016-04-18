
from redcmd.api import subcmd

from .base import ConfigSubcommand


class SourceStateSubcommands(ConfigSubcommand):

	@subcmd
	def enable(self, name):
		pass


	@subcmd
	def disable(self, name):
		pass



