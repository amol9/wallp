import shutil
import tempfile
from os.path import join as joinpath, exists
from time import time
from os import stat
from datetime import datetime, timedelta

from redlib.api.system import *
from redlib.api.image import get_image_info
from mayloop.transport.pipe_connection import PipeConnection

from util.retry import Retry
from util.logger import log
from db import Image, Config
from globals import Const
from desktop import DesktopError, get_desktop
from desktop.wpstyle import WPStyle, compute_style
from server.protocol import WPState
from db import GlobalVars, VarError
from util.printer import printer
from source.source_factory import SourceFactory, SourceFactoryError
from source.base import SourceError, SourceParams


# for outside of this module
class WallpaperError(Exception):
	pass


# for this module only
class GetImageError(Exception):
	pass


class Wallpaper:

	def __init__(self, params=None, transport=None):
		self._params = params if params is not None else SourceParams()
		self._transport = None


	def change(self):
		self.check_keep_timeout()

		transport = self._transport
		try:
			self.write_to_transport(WPState.CHANGING)

			source, source_response = self.get_image()
			wp_image_path = self.move_temp_file(source_response)

			im_type, im_width, im_height = get_image_info(None, filepath=wp_image_path)

			dt = get_desktop()
			wp_style = compute_style(im_width, im_height, *dt.get_size())

			dt.set_wallpaper(wp_image_path, style=wp_style)
			printer.printf('wallpaper changed', '', verbosity=2)

			image_id = self.save_image_info(source_response.db_image, source, wp_image_path, source_response.url, im_type, im_width, im_height)
			self.update_global_vars(image_id)

			self.write_to_transport(WPState.READY)
			self.write_to_transport(wp_image_path)
		
		except DesktopError as e:
			log.error('error while changing wallpaper')
			raise WallpaperError(str(e))

		except GetImageError as e:
			log.error(str(e))
			self.write_to_transport(WPState.ERROR)
			raise WallpaperError(str(e))


	def write_to_transport(self, msg):
		transport = self._transport

		if transport is not None:
			transport.write_blocking(msg)


	def check_keep_timeout(self):
		try:
			keep_timeout = GlobalVars().get('keep_timeout')
		except VarError as e:
			log.error(str(e))

		if keep_timeout is not None and keep_timeout > time():
			expiry = datetime.fromtimestamp(keep_timeout).strftime('%d %b %Y, %H:%M:%S')
			msg = 'current wallpaper is set not to change until %s'%expiry
			log.error(msg)
			raise WallpaperError(msg)


	def update_global_vars(self, image_id):
		globalvars = GlobalVars()
		try:
			globalvars.set('current_wallpaper_image', image_id)
			globalvars.set('last_change_time', int(time()))
		except VarError as e:
			log.error(str(e))


	def get_image(self):
		retry = Retry(retries=3, final_exc=GetImageError())

		while retry.left():
			try:
				source = self.get_source()
				source_response = source.get_image(params=self._params)
				retry.cancel()

			except SourceError as e:
				log.error(e)

				if self._params.name is not None:
					retry.cancel()
					raise GetImageError(str(e))
				else:
					printer.printf('error', str(e))
					retry.retry()

		return source, source_response


	def get_source(self):
		try:
			source_factory = SourceFactory()
			source = source_factory.get(self._params.name)
			printer.printf('source', source.name)
			return source
		except SourceFactoryError as e:
			log.error(e)
			raise WallpaperError(str(e))


	def move_temp_file(self, source_response):
		if source_response.filepath is not None:
			return source_response.filepath

		dirpath = get_pictures_dir() if not Const.debug else '.'
		wp_path = joinpath(dirpath, Const.wallpaper_basename + '.' + source_response.ext)

		try:
			shutil.move(source_response.temp_filepath, wp_path)
		except (IOError, OSError) as e:
			log.error(str(e))
			raise GetImageError(str(e))

		return wp_path


	def save_image_info(self, db_image, source, wp_path, image_url, image_type, image_width, image_height):
		if db_image is None:
			image = Image()
		else:
			image = db_image

		image.type = image_type
		image.width = image_width
		image.height = image_height

		image.size = stat(wp_path).st_size

		image.filepath = wp_path
		image.time = int(time())

		if db_image is None:
			image.url = image_url

			image_context = source.image_context
			image.title = image_context.title
			image.description = image_context.description[0: 1024] if image_context.description is not None else None
			image.context_url = image_context.url
			image.artist = image_context.artist

			image.trace = source.image_trace

		image.save()
		return image.id

