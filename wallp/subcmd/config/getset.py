
from redcmd.api import subcmd, Arg, CommandError

from .base import ConfigSubcommand
from ...util.printer import printer
from ...util import log
from ...db.app.config import Config, ConfigError
from ...db.app.sources import Sources, DBSourceError


__all__ = ['GetSetSubcommands']


class GetSetSubcommands(ConfigSubcommand):

	def __init__(self):
		self._config = Config()


	@subcmd
	def get(self, name):
		'''Print value of a configuration setting.
		name:	name of the setting'''

		print(self.exc_call(self._config.sget, name))


	@subcmd
	def set(self, name, value):
		'''Set value of a configuration setting.
		name:	name of the setting'''

		self.exc_call(self._config.sset, name, value, check_type=True)
		print('setting changed')


	@subcmd
	def log(self, filename, level=Arg(choices=list(log.levels.keys()), default='error', opt=True)):
		'''Set log file and log level.
		filename: 	file for storing the log
				use "stdout" to print it to screen
		level: 		log level'''

		self.exc_call(self._config.eset, 'client.logfile', filename)
		self.exc_call(self._config.eset, 'client.loglevel', log.levels[level])


	@subcmd
	def dump(self):
		'Print all the configuration settings.'


		settings = self.exc_call(self._config.get_all)
		for name, value in settings:
			printer.printf(name, str(value))

		printer.printf('', '')

		try:
			sources = Sources()
			source_states = sources.get_all()
		except DBSourceError as e:
			print(e)
			raise CommandError()

		for name, enabled in source_states:
			printer.printf(name, 'enabled' if enabled else 'disabled')


	def exc_call(self, method, *args, **kwargs):
		try:
			return method(*args, **kwargs)
		except ConfigError as e:
			print(e)
			raise CommandError()

