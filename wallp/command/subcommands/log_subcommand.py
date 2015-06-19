
from ..subcommand import Subcommand, subcmd, Choices
from ...util import log
from ...db import Config
from ..exc import CommandError


class LogSubcommand(Subcommand):
	level_choices = Choices(log.levels.keys(), default='debug')

	@subcmd
	def log(self, filename, level=level_choices):
		config = Config()
		config.set('client.logfile', filename)
		config.set('client.loglevel', log.levels[level])
