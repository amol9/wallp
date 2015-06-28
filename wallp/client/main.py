import sys

from ..version import __version__
from ..command import Command
from .init import first_run, start_log, InitError
from ..db.exc import DBError


#entry point
def main():
	try:
		first_run()
		start_log()
	except (InitError, DBError) as e:
		print(e)
		sys.exit(1)

	command = Command()
	command.add_version(__version__)
	command.set_default_subcommand('change')
	command.execute()

