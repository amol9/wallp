from argparse import ArgumentParser

from ..version import __version__
from ..util import Scheduler
from . import change_wallpaper, CWSpec


class ArgParser:
	def __init__(self):
		self.add_args()


	def add_args(self):
		self._argparser = ArgumentParser()

		self._argparser.add_argument('-v', '--version', action='version', version=__version__, help='print version')
		
		subparsers = self._argparser.add_subparsers(dest='subcommand')

		self.add_subcmd_change(subparsers)
		self.add_subcmd_schedule(subparsers)
		self.add_subcmd_set(subparsers)
		self.add_subcmd_get(subparsers)
		self.add_subcmd_add(subparsers)
		

	def add_subcmd_change(self, subparsers):
		change_parser = subparsers.add_parser('change')

		change_parser.add_argument('-s', '--service', help='service to be used (' +
				''.join([s.name + ', ' for s in service_factory.services[0:-1]]) + service_factory.services[-1].name + ')')
		change_parser.add_argument('-q', '--query', help='search term')
		change_parser.add_argument('-c', '--color', help='color')


	def add_subcmd_schedule(self, subparsers):
		schedule_parser = subparsers.add_parser('schedule')


	def add_subcmd_set(self, subparsers):
		set_parser = subparsers.add_parser('set')

		set_parser.add_argument('name', help='setting name')
		set_parser.add_argument('value', help='setting value')


	def add_subcmd_get(self, subparsers):
		get_parser = subparsers.add_parser('get')

		get_parser.add_argument('name', help='setting name')


	def add_subcmd_add(self, subparsers):
		add_parser = subparsers.add_parser('add')

		add_parser.add_argument('list_name', help='list name')
		add_parser.add_argument('value', help='item value')



	def dispatch(self):
		try:
			#do command
		except AppError as e:
			log.error(str(e))
			sys.exit(1)



