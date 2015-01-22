from os.path import join as joinpath
import sys
from argparse import ArgumentParser, HelpFormatter
import os

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
		argparser = ArgumentParser(formatter_class=MultilineFormatter)
		argparser.add_argument('-s', '--service', help='service to be used (' +
				''.join([s.name + ', ' for s in service_factory.services[0:-1]]) + service_factory.services[-1].name + ')')
		argparser.add_argument('-q', '--query', help='search term for wallpapers')
		argparser.add_argument('-c', '--color', help='color')
		argparser.add_argument('-f', '--frequency', help='R|set the frequency for update' + os.linesep + scheduler_help_text)

		self._args = argparser.parse_args()


	def set_frequency(self):
		freq = self._args.frequency
		if freq is not None:
			if freq == '0':
				get_scheduler().delete()
			else:
				get_scheduler().delete()
				get_scheduler().schedule(freq)
			sys.exit(0)


	def change_wallpaper(self):
		self._wp_path = None
		self._style = None
		self.get_image()
		self.set_as_wallpaper()
			

	def get_image(self):
		service = None

		service_name = self._args.service
		query = self._args.query

		retry = 3
		while(retry > 0):
			if service_name == None:
				service = service_factory.get_random()
			else:
				service = service_factory.get(service_name)
				if service is None:
					log.info('unknown service or service is disabled')
					return
			log.info('using %s'%service.name)
			
			try:
				color = None
				if service.name == 'bitmap':
					self._style = 'tiled'
					color = self._args.color
				else:
					self._style = 'zoom'

				temp_basename = 'wallp_temp'
				dirpath = get_pictures_dir() if not Const.debug else '.'
				
				tempname = service.get_image(dirpath, temp_basename, query=query, color=color)
				self._wp_path = joinpath(dirpath, Const.wallpaper_basename + tempname[tempname.rfind('.'):])
				os.rename(joinpath(dirpath, tempname), self._wp_path)


				retry = 0
			except ServiceException:
				log.error('error accessing %s'%service.name)
				retry = 0 if service_name else retry - 1
	

	def set_as_wallpaper(self):
		if self._wp_path is None:
			return

		dt = get_desktop()
		dt.set_wallpaper(self._wp_path)
		dt.set_wallpaper_style(self._style)


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




