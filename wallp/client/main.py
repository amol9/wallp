import sys

from ..version import __version__
from . import ArgParser
from ..command import Command


#entry point
def main():
	command = Command()
	command.add_version(__version__)
	command.set_default_subcommand('change')
	command.execute()

