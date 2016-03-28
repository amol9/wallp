
from redcmd.api import Subcommand, subcmd, Arg, CommandError

from ..util import log
from ..db.app.config import Config


__all__ = ['LogSubcommand']


class LogSubcommand(Subcommand):

	@subcmd
	def log(self, filename, level=Arg(choices=list(log.levels.keys()), default='debug')):
		'''Set log file and log level.
		filename: 	file to store the log, use "stdout" to just print it to screen
		level: 		log level'''

		config = Config()
		config.set('client.logfile', filename)
		config.set('client.loglevel', log.levels[level])

