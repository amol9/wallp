from argparse import ArgumentParser
import logging

from ..version import __version__
from ..util import Scheduler
from . import change_wallpaper, CWSpec
from ..service import service_factory


class MultilineFormatter(HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        return HelpFormatter._split_lines(self, text, width)


class ArgParser:
	def __init__(self):
		self.add_args()


	def add_args(self):
		self._argparser = ArgumentParser(formatter_class=MultilineFormatter)

		self._argparser.add_argument('-v', '--version', action='version', version=__version__, help='print version')
		
		subparsers = self._argparser.add_subparsers(dest='subcommand')

		self.add_subcmd_change(subparsers)
		self.add_subcmd_schedule(subparsers)
		self.add_subcmd_set(subparsers)
		self.add_subcmd_get(subparsers)
		self.add_subcmd_add(subparsers)


	def parse_args(self):
		args = self._argparser.parse_args()
		self.dispatch(args)
		

	def add_subcmd_change(self, subparsers):
		change_parser = subparsers.add_parser('change')

		service_list = ', '.join([s.name for s in service_factory.services])
		change_parser.add_argument('-s', '--service', help='one of (%s)'%service_list)
		change_parser.add_argument('-q', '--query', help='search term')
		change_parser.add_argument('-c', '--color', help='color')

		change_parser.set_defaults(func=self._subcommands.change)


	def add_subcmd_schedule(self, subparsers):
		schedule_parser = subparsers.add_parser('schedule')

		schedule_parser.set_defaults(func=self._subcommands.schedule)


	def add_subcmd_log(self, subparsers):
		log_parser = subparsers.add_parser('log')
		
		logging_levels = None
		if is_py3():
			logging_levels = dict(chain(logging._nameToLevel.items(), logging._levelToName.items()))
		else:
			logging_levels = logging._levelNames

		choices = [v.lower() for (k, v) in list(logging_levels.items()) if type(k) == int and k > 0]

		log_parser.add_argument('filename', default='stdout', help='filename for logging or none for standard output')
		log_parser.add_argument('-l', '--level', choices=choices)

		log_parser.set_defaults(func=self._subcommands.log)


	def add_subcmd_set(self, subparsers):
		set_parser = subparsers.add_parser('set')

		set_parser.add_argument('name', help='setting name')
		set_parser.add_argument('value', help='setting value')

		set_parser.set_defaults(func=self._subcommands.set)


	def add_subcmd_get(self, subparsers):
		get_parser = subparsers.add_parser('get')

		get_parser.add_argument('name', help='setting name')

		get_parser.set_defaults(func=self._subcommands.get)


	def add_subcmd_add(self, subparsers):
		add_parser = subparsers.add_parser('add')

		add_parser.add_argument('list_name', help='list name')
		add_parser.add_argument('value', help='item value')

		add_parser.set_defaults(func=self._subcommands.add)


	def dispatch(self, args):
		try:
			self._subcommands.args = args
			args.func()
		except AppError as e:
			log.error(str(e))
			sys.exit(1)

		sys.exit(0)

