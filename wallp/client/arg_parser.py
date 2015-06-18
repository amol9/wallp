from argparse import ArgumentParser, HelpFormatter
import logging
import sys

from mutils.system import *

from ..version import __version__
from ..service import service_factory
from ..db import func as dbfunc
from .subcommands import Subcommands, AppError
from ..globals import Const
from ..util import log


class MultilineFormatter(HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        return HelpFormatter._split_lines(self, text, width)


class ArgParser:
	def __init__(self):
		self._subcommands = Subcommands()
		self.add_args()


	def add_args(self):
		self._argparser = ArgumentParser(formatter_class=MultilineFormatter, prog='wallp',
						description='A command line utility to download wallpapers from various sources.')

		self._argparser.add_argument('-v', '--version', action='version', version=__version__, help='print version')
		
		subparsers = self._argparser.add_subparsers(dest='subcommand')

		self.add_subcmd_change(subparsers)
		self.add_subcmd_schedule(subparsers)
		self.add_subcmd_log(subparsers)
		self.add_subcmd_set(subparsers)
		self.add_subcmd_get(subparsers)
		self.add_subcmd_add(subparsers)
		self.add_subcmd_enable(subparsers)
		self.add_subcmd_disable(subparsers)
		self.add_subcmd_like(subparsers)
		self.add_subcmd_dislike(subparsers)
		self.add_subcmd_keep(subparsers)
		self.add_subcmd_info(subparsers)
		self.add_subcmd_db(subparsers)


	def parse_args(self):
		if len(sys.argv) == 1:
			sys.argv.append('change')
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
		schedule_parser.add_argument('frequency')
		schedule_parser.set_defaults(func=self._subcommands.schedule)


	def add_subcmd_log(self, subparsers):
		log_parser = subparsers.add_parser('log')
		
		log_parser.add_argument('filename', default='stdout', help='filename for logging or none for standard output')
		log_parser.add_argument('-l', '--level', choices=log.levels.keys())

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


	def add_list_subcmd(self, subparsers, subcmd, func):
		subcmd_parser = subparsers.add_parser(subcmd)

		list_names = [l.name for l in dbfunc.get_lists()]
		subcmd_parser.add_argument('list_name', choices=list_names, help='list name')
		subcmd_parser.add_argument('item', help='item value')

		subcmd_parser.set_defaults(func=func)


	def add_subcmd_add(self, subparsers):
		self.add_list_subcmd(subparsers, 'add', self._subcommands.add)


	def add_subcmd_enable(self, subparsers):
		self.add_list_subcmd(subparsers, 'enable', self._subcommands.enable)


	def add_subcmd_disable(self, subparsers):
		self.add_list_subcmd(subparsers, 'disable', self._subcommands.disable)


	def add_subcmd_like(self, subparsers):
		like_parser = subparsers.add_parser('like')
		like_parser.set_defaults(func=self._subcommands.like)


	def add_subcmd_dislike(self, subparsers):
		dislike_parser = subparsers.add_parser('dislike')
		dislike_parser.add_argument('-n', '--dont-change', action='store_true', help='don\'t change the wallpaper') 
		dislike_parser.set_defaults(func=self._subcommands.dislike)


	def add_subcmd_keep(self, subparsers):
		keep_parser = subparsers.add_parser('keep')
		keep_parser.add_argument('period', help='keep wallpaper for specified time')
		keep_parser.set_defaults(func=self._subcommands.keep)


	def add_subcmd_info(self, subparsers):
		info_parser = subparsers.add_parser('info')
		#info_parser.add_argument('filename', default=None)
		info_parser.set_defaults(func=self._subcommands.info)


	def add_subcmd_db(self, subparsers):
		db_parser = subparsers.add_parser('db')

		dbsubparsers = db_parser.add_subparsers(dest='dbsubcommand')

		db_reset_parser = dbsubparsers.add_parser('reset')
		db_reset_parser.set_defaults(func=self._subcommands.db_reset)

		db_backup_parser = dbsubparsers.add_parser('backup')
		db_backup_parser.add_argument('destpath')
		db_backup_parser.set_defaults(func=self._subcommands.db_backup)


	def dispatch(self, args):
		try:
			#import pdb; pdb.set_trace()
			self._subcommands.args = args
			self._subcommands.start_log()
			self._subcommands.add_config_shortcuts()
			args.func()
		except AppError as e:
			sys.exit(1)

		sys.exit(0)

