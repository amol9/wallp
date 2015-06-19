from argparse import ArgumentParser


class Command(object):
	'Command line handler.'

	def __init__(self):
		self.argparser = ArgumentParser(prog='wallp',
						description='A command line utility to download wallpapers from various sources.')

		self.add_subcommands()

	
	def add_subcommands(self):
		for subcmd_cls in self.__class__.__subclasses__():
			subcmd_cls(self.argparser)



	def execute(self):
		self.argparser.parse_args()
		print 'not implemented'


	def add_version(self, version):
		self.argparser.add_argument('-v', '--version', action='version', version=version, help='print version')
