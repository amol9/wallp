from os.path import join as joinpath
import sys
from argparse import ArgumentParser
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


class Manager():
	def __init__(self):
		if not exists(Const.data_dir):
			mkdir(Const.data_dir)
		self.parse_args()
		self.set_frequency()


	def parse_args(self):
		argparser = ArgumentParser()
		argparser.add_argument('-s', '--service', help='service to be used (' +
				''.join([s.name + ', ' for s in service_factory.services[0:-1]]) + service_factory.services[-1].name + ')')
		argparser.add_argument('-q', '--query', help='search term for wallpapers')
		argparser.add_argument('-c', '--color', help='color')
		argparser.add_argument('-f', '--frequency', help='set the frequency for update' + os.linesep + scheduler_help_text)

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
			log.info('using service: %s'%service.name)
			
			try:
				#self._wallpaper_filename = service.get_image(get_pictures_dir(), Const.wallpaper_basename)
				self._wallpaper_filename = service.get_image('.', Const.wallpaper_basename, query)
				retry = 0
			except ServiceException:
				log.error('error accessing %s'%service.name)
				retry = 0 if service_name else retry - 1
	

	def set_as_wallpaper(self):
		dt = desktop.get_desktop()
		#dt.set_wallpaper(joinpath(get_pictures_dir(), self._wallpaper_filename))


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




