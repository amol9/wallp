from os.path import join as joinpath
import sys
from argparse import ArgumentParser, HelpFormatter
import os
from shutil import move
import logging
from itertools import chain

from wallp.reddit import Reddit
from wallp.deviantart import DeviantArt
from wallp.bing import Bing
from wallp.imgur import Imgur
from wallp.google import Google
from wallp.bitmap import Bitmap
from wallp.globals import Const
from wallp.service import service_factory, ServiceException
from wallp.logger import log
from wallp.system import *
from wallp.scheduler import get_scheduler, help as scheduler_help_text
from wallp.desktop import get_desktop
from wallp.imageinfo import get_image_info


class MultilineFormatter(HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        return HelpFormatter._split_lines(self, text, width)


class Manager():
	def __init__(self):
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
		argparser.add_argument('-s', '--service', help='service to be used (' +
				''.join([s.name + ', ' for s in service_factory.services[0:-1]]) + service_factory.services[-1].name + ')')
		argparser.add_argument('-q', '--query', help='search term for wallpapers')
		argparser.add_argument('-c', '--color', help='color')
		argparser.add_argument('-l', '--log', help='logfile name / stdout')
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

		cmd = ''.join([arg + ' ' for arg in sys.argv])

		if freq == '0':
			get_scheduler().delete(Const.scheduler_task_name)
		else:
			get_scheduler().delete(Const.scheduler_task_name)
			get_scheduler().schedule(freq, cmd, Const.scheduler_task_name)

		sys.exit(0)


	def change_wallpaper(self):
		self._wp_path = None
		self._style = None
		self.get_image()
		self.set_as_wallpaper()
		if is_py3(): print('')
			

	def get_image(self):
		service = None

		service_name = self._args.service

		retry = 3
		while(retry > 0):
			if service_name == None:
				service = service_factory.get_random()
			else:
				service = service_factory.get(service_name)
				if service is None:
					log.info('unknown service or service is disabled')
					return
			prints(service.name)
			if log.to_stdout(): print('')
			
			try:
				color = self._args.color
				query = self._args.query

				temp_basename = 'wallp_temp'
				dirpath = get_pictures_dir() if not Const.debug else '.'
				
				tempname = service.get_image(dirpath, temp_basename, query=query, color=color)
				self._wp_path = joinpath(dirpath, Const.wallpaper_basename + tempname[tempname.rfind('.'):])
				move(joinpath(dirpath, tempname), self._wp_path)


				retry = 0
			except ServiceException:
				log.error('error accessing %s'%service.name)
				retry = 0 if service_name else retry - 1
	

	def set_as_wallpaper(self):
		if self._wp_path is None:
			return

		dt = get_desktop()
		
		dt_width, dt_height = dt.get_size()
		log.debug('desktop: width=%d, height=%d'%(dt_width, dt_height))

		style = None
		buf = None
		with open(self._wp_path, 'rb') as f:
			buf = f.read(10000)

		_, wp_width, wp_height = get_image_info(buf, filepath=self._wp_path)
		log.debug('iamge: width=%d, height=%d'%(wp_width, wp_height))

		if wp_width < 5 and wp_height < 5:
			style = 'tiled'
		else:
			same_ar = False
			dt_ar = float(dt_width) / dt_height
			wp_ar = float(wp_width) / wp_height
			
			if abs(dt_ar - wp_ar) < 0.01:
				same_ar = True	
	
			#import pdb; pdb.set_trace()		
			wr = float(wp_width) / dt_width
			hr = float(wp_height) / dt_height

			if (wr >= 0.9) and (hr >= 0.9):
				style = 'scaled' if same_ar else 'zoom'
			elif (wr < 0.9) or (hr < 0.9):
				style = 'centered'
			else:
				style = 'scaled' if same_ar else 'zoom' 

		log.debug('style: %s'%style)
		dt.set_wallpaper_style(style)
		dt.set_wallpaper(self._wp_path)

	#def set_image_as_desktop_back(self):
		'''
		iinfo = check_output(['identify', imagepath])

		id_regex = re.compile(".*\s+(\d+)x(\d+)\s+.*")
		m = id_regex.match(iinfo)

		picture_options = None
		if m:
			iwidth = m.group(1)
			iheight = m.group(2)
			print 'image w = ', iwidth, ' height = ', iheight
			
			if iwidth > self._width or iheight > self._height:
				picture_options = 'scaled'
			else:
				picture_options = 'centered'
		'''




