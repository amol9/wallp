
from ..subcommand import Subcommand, subcmd
from ...util import log
from ...db import Config


class LogSubcommand(Subcommand):

	@subcmd
	def log(self, filename, level=Choices(log.levels.keys())):
		config = Config()
		config.set('client.logfile', filename)
		config.set('client.loglevel', log.levels[level])
