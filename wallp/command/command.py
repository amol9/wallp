import sys

from .exc import CommandError
from .command_help_formatter import CommandHelpFormatter
from .commandparser import CommandParser


class Command(object):
	'Command line handler.'

	def __init__(self):
		self.argparser = CommandParser(prog='wallp',
						description='A command line utility to download wallpapers from various sources.',
						formatter_class=CommandHelpFormatter)

		self.default_subcommand = None
		self.formatter_class = CommandHelpFormatter
		self.add_subcommands()

	
	def add_subcommands(self):
		for subcmd_cls in self.__class__.__subclasses__():
			subcmd_cls(self.argparser)


	def execute(self):
		if self.default_subcommand is not None and len(sys.argv) == 1 :
			sys.argv.append(self.default_subcommand)

		args = self.argparser.parse_args()
		try:
			subcmd_func = args.subcmd_func
			subcmd_func.execute(args)
		except CommandError as e:
			sys.exit(1)

		sys.exit(0)


	def add_version(self, version):
		self.argparser.add_argument('-v', '--version', action='version', version=version, help='print program version')

	
	def set_default_subcommand(self, name):
		self.default_subcommand = name

