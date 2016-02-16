from importlib import import_module
import sys
import platform


def setup_autocomp(commands_module, command_name, _to_hyphen=False):
	if platform.system() != 'Linux':
		return

	args = sys.argv

	if len(args) > 1 and args[1] == 'install':
		rc_api = None
		try:
			rc_api = import_module('redcmd.api')
		except ImportError as e:
			print('cannot setup autocomplete for %s'%command_name)
			return
		
		rc_api.setup_autocomp(commands_module, command_name, _to_hyphen=_to_hyphen)
		print('autocomplete setup for %s'%command_name)

