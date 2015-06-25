import sys

from ..version import __version__
from ..command import Command
from .init import first_run, start_log


#entry point
def main():
	first_run()
	start_log()

	command = Command()
	command.add_version(__version__)
	command.set_default_subcommand('change')
	command.execute()

