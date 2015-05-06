from os.path import join as joinpath
import os
import sys
import logging
from itertools import chain
from argparse import ArgumentParser, HelpFormatter
import socket
from time import sleep

from mutils.system import *

from .globals import Const
from .version import __version__
from .desktop_factory import get_desktop, DesktopException
from .deviantart import DeviantArt
from .service import service_factory, ServiceException
from .scheduler import get_scheduler, help as scheduler_help_text
from .helper import get_image, compute_style
from .logger import log


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


	def set_frequency(self):
		freq = self._args.frequency
		if freq is None:
			return

		def find_arg(val):
			try:
				return sys.argv.index(val)
			except ValueError:
				return -1

		fpos = find_arg('-f')
		fpos = find_arg('--frequency') if fpos == -1 else fpos

		del sys.argv[fpos]
		del sys.argv[fpos]

		cmd = Const.scheduler_cmd + ' ' + ' '.join([arg for arg in sys.argv[1:]])

		taskname = Const.scheduler_task_name
		sch = get_scheduler()
		if freq == '0':
			if sch.exists(taskname):
				r = sch.delete(taskname)
				print('schedule deletion %s..'%('succeeded' if r else 'failed'))
			else:
				print('no schedule exists..')
		else:
			if sch.exists(taskname):
				sch.delete(taskname)
			r = sch.schedule(freq, cmd, taskname)
			print('schedule creation %s..'%('succeeded' if r else 'failed'))
		sys.exit(0)


	def change_wallpaper(self, from_server=None):
		try:
			wp_path = get_image(service_name=self._args.service, query=self._args.query, color=self._args.color)
			style = compute_style(wp_path)

			dt = get_desktop()
			dt.set_wallpaper(wp_path, style=style)
		
		except DesktopException:
			log.error('cannot change wallpaper')

		if is_py3(): print('')


	def get_image_from_wallp_server(self, server_addr):
		host, port = server_addr.split(',')
		port = int(port)

		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.connect((host, port))

		conn.send('wallp\n\r')

		def read_response(length=None):
			data = ''
			if length is not None:
				condition = lambda d : len(d) < length
			else:
				condition = lambda d : not d.endswith('\n\r')

			while True:
				chunk = conn.recv(1024)
				if chunk is None or len(chunk) == 0:
					break
				print 'client recvd chunk: ', chunk
				data += chunk

			return data

		#import pdb; pdb.set_trace()
		data = read_response()

		retries = 3
		while retries > 0:
			if data.startswith('in-progress'):
				print 'try again'
				retries -= 1
				sleep(10)

			elif data.startswith('image-ext'):
				retries = 0
				#print data
				#image_len = int(read_response().strip().splot(':').strip())
				#image = read_response(length=image_len)
				image_ext_end = data.find('\n\r')
				print 'ext: ' , data[0 : image_ext_end]

				image_len_end = data.find('\n\r', image_ext_end + 2)
				print 'len: ', data[image_ext_end + 2 : image_len_end]

				image = data[image_len_end + 2 : ]
				print 'image size: ', len(image)

		
