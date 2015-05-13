from os.path import join as joinpath
import os
import sys
import logging
from itertools import chain
from argparse import ArgumentParser, HelpFormatter
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
		msg_receiver = MessageReceiver(blocking=True)

		request = Request()

		request.type = Request.IMAGE
		conn.send(prefix_message_length(request.SerializeToString()))

		def read_response(length=None):
			message = msg_receiver.recv(conn)
			response = Response()
			response.ParseFromString(message)
			return response


		done = False
		image = ''
		chunks = 0
		retries = 3
		while not done:
			response = read_response()

			if response.type == Response.IMAGE_CHANGING:
				print 'try again'
				sleep(10)
				retries -= 1

				if retries > 0:
					conn.send(prefix_message_length(request.SerializeToString()))
				else:
					done = True

			elif response.type == Response.IMAGE_NONE:
				print 'image none'
				done = True

			elif response.type == Response.IMAGE_INFO:
				image_info = response.image_info

				print 'ext: ', image_info.extension
				print 'len: ', image_info.length
				chunks = image_info.chunks
				print 'chunks: ', chunks

			elif response.type == Response.IMAGE_CHUNK:
				image_chunk = response.image_chunk
				image += image_chunk.data
				print 'chunk len: ', len(image_chunk.data)
				chunks -= 1
				
				if chunks == 0:
					done = True

			else:
				print 'bad response'
				done = True
