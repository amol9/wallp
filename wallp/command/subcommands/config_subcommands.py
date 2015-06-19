
from ..subcommand import Subcommand, subcmd
from ...util import Config, ConfigError


class ConfigSubcommands(Subcommand):

	@subcmd
	def get(self, name):
		config = Config()
		value = self.config_call(config.get, name)
		print(value)


	@subcmd
	def set(self, name, value):
		config = Config()
		self.config_call(config.set, name, value)
	
	
	def config_call(self, func, *args):
		try:
			r = func(*args)
			return r
		except ConfigError as e:
			print(str(e))
			raise AppError()

