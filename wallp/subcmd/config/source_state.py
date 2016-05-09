
from redcmd.api import subcmd, Arg, CommandError

from .base import ConfigSubcommand
from ...db.app.sources import Sources, DBSourceError
from ...source.source_factory import SourceFactory


source_names = SourceFactory().source_names


class SourceStateSubcommands(ConfigSubcommand):

	def __init__(self):
		self._sources = Sources()


	def name(self, name=Arg(choices=source_names + ['all'], default=None, opt=False)):
		'''name: 	name of the source
				"all" for changing all sources'''

		self._arg_name = name


	@subcmd(add=[name])
	def enable(self):
		'Enable a source.'
		self.apply_all(True)


	@subcmd(add=[name])
	def disable(self):
		'Disable a source.'
		self.apply_all(False)


	def apply_all(self, enabled):
		method = self._sources.enable if enabled else self._sources.disable
		action_str = 'enabled' if enabled else 'disabled'

		if self._arg_name == 'all':
			list(map(lambda n : self.exc_call(method, n), source_names))
			msg = 'all sources %s'%action_str
		else:
			self.exc_call(method, self._arg_name)
			msg = '%s %s'%(self._arg_name, action_str)

		print(msg)


	def exc_call(self, method, *args):
		try:
			method(*args)
		except DBSourceError as e:
			print(e)
			raise CommandError()

