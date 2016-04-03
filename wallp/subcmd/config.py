import os

from redcmd.api import Subcommand, subcmd, CommandError

from ..db.app.config import Config, ConfigError
from .. import const


__all__ = ['ConfigSubcommands']


class ConfigSubcommands(Subcommand):

	def __init__(self):
		#super(ConfigSubcommands, self).__init__(parser)
		self.add_config_shortcuts()

	
	def add_config_shortcuts(self):
		config = Config()
		config.add_shortcut('server', ['server.host', 'server.port'], [None, const.default_server_port], ':')

		setting_names = config.names
		config.add_shortcut('all', setting_names, None, os.linesep, get_only=True, print_fmt=True)


	@subcmd
	def get(self, name):
		'''Print value of a setting.
		name: name of the setting. "all" for printing values for all settings.'''

		config = Config()
		value = self.config_call(config.get, name)
		print(value)


	@subcmd
	def set(self, name, value):
		'''Assign a value to a setting.
		name: 	name of the setting.
		value: 	value of the setting'''

		config = Config()
		self.config_call(config.set, name, value)
	
	
	def config_call(self, func, *args):
		try:
			r = func(*args)
			return r
		except (ConfigError, ValueError) as e:
			print(str(e))
			raise CommandError()

