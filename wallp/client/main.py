import sys

from redcmd.api import commandline_execute

from ..version import __version__
from .init import first_run, start_log, InitError
from ..db.exc import DBError
from ..subcmd import all


#entry point
def main():
	try:
		first_run()
		start_log()
	except (InitError, DBError) as e:
		print(e)
		sys.exit(1)

	commandline_execute(	prog='wallp',
				description='A command line utility to download and set wallpapers from various sources.',
				version=__version__,
				_to_hyphen=True,
				default_subcommand='change',
				moves=True)

