
from redcmd.api import subcmd

from .base import ConfigSubcommand


class GetSetSubcommands(ConfigSubcommand):

	@subcmd
	def get(self, name):
		pass


	@subcmd
	def set(self, name, value):
		pass


	@subcmd
	def log(self, filename, level):
		pass


	@subcmd
	def dump(self):
		pass

