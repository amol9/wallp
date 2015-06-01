from os.path import join as joinpath
import os
import sys
import logging
from itertools import chain
from argparse import ArgumentParser, HelpFormatter
from time import sleep

from mutils.system import *

from ..globals import Const
from ..version import __version__
from ..desktop.desktop_factory import get_desktop, DesktopException
from ..service import service_factory, ServiceException
from ..util.scheduler import get_scheduler, help as scheduler_help_text
from .helper import get_image, compute_style
from ..util.logger import log



class MultilineFormatter(HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        return HelpFormatter._split_lines(self, text, width)


#todo: rename to Client, remove unnecessary imports
class Manager():
	def __init__(self):
		log.debug('[start]')
		if not exists(Const.data_dir):
			mkdir(Const.data_dir)
		self.parse_args()
		self.set_frequency()


	def parse_args(self):
		logging_levels = None
		if is_py3():
			logging_levels = dict(chain(logging._nameToLevel.items(), logging._levelToName.items()))
		else:
			logging_levels = logging._levelNames
	
		argparser = ArgumentParser(formatter_class=MultilineFormatter)

		argparser.add_argument('-v', '--version', action='version', version=__version__, help='print version')
		argparser.add_argument('-s', '--service', help='service to be used (' +
				''.join([s.name + ', ' for s in service_factory.services[0:-1]]) + service_factory.services[-1].name + ')')
		argparser.add_argument('-q', '--query', help='search term for wallpapers')
		argparser.add_argument('-c', '--color', help='color')
		argparser.add_argument('-l', '--log', default='stdout', help='logfile name / stdout')
		argparser.add_argument('-ll', '--loglevel',
			choices=[v.lower() for (k, v) in list(logging_levels.items()) if type(k) == int and k > 0], help='log level')
		argparser.add_argument('-f', '--frequency', help='R|set the frequency for update' + os.linesep + scheduler_help_text)

		self._args = argparser.parse_args()

		if self._args.log:
			if self._args.loglevel:
				log.start(self._args.log, loglevel=logging_levels[self._args.loglevel.upper()])
			else:
				log.start(self._args.log)


	
