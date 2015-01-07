from os.path import join as joinpath
import sys

from wallp.reddit import Reddit
from wallp.deviantart import DeviantArt
from wallp.bing import Bing
from wallp.imgur import Imgur
from wallp.google import Google
from wallp.globals import Const
from wallp.service import service_factory, ServiceException
from wallp.logger import log
from wallp.system import *

class Manager():

	def get_image(self, site=None, choice=None):
		service = None

		retry = 3
		while(retry > 0):
			if site == None:
				service = service_factory.get_random()
			else:
				service = service_factory.get(site)
			log.info('using service: %s'%service.name)
			
			try:
				#self._wallpaper_filename = service.get_image(get_pictures_dir(), Const.wallpaper_basename)
				self._wallpaper_filename = service.get_image('.', Const.wallpaper_basename, choice)
				retry = 0
			except ServiceException:
				log.error('error accessing %s'%service.name)
				retry = 0 if site else retry - 1
	

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




