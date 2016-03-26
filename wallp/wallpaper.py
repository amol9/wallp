import shutil
import tempfile
from os.path import join as joinpath, exists
from time import time
from os import stat
from datetime import datetime, timedelta

from redlib.api.system import *
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

			source, image = self.get_image()

			wp_image_path = self.move_temp_file(image)

			dt = get_desktop()
			wp_style = compute_style(image.i_width, image.i_height, *dt.get_size())

			dt.set_wallpaper(wp_image_path, style=wp_style)
			printer.printf('wallpaper changed', '', verbosity=2)

			image_id = self.save_image_info(source, wp_image_path, image)
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
				image = source.get_image(params=self._params)
				retry.cancel()

			except SourceError as e:
				log.error(e)

				if self._params.name is not None:
					retry.cancel()
					raise GetImageError(str(e))
				else:
					printer.printf('error', str(e), verbosity=2)
					retry.retry()

		return source, image


	def get_source(self):
		try:
			source_factory = SourceFactory()
			source = source_factory.get(self._params.name)
			if source is None:
				raise SourceError('error getting source')

			printer.printf('source', source.name)
			return source
		except SourceFactoryError as e:
			log.error(e)
			raise WallpaperError(str(e))


	def move_temp_file(self, image):
		if image.filepath is not None:
			return image.filepath

		dirpath = get_pictures_dir() if not Const.debug else '.'
		wp_path = joinpath(dirpath, Const.wallpaper_basename + '.' + image.ext)

		try:
			shutil.move(image.temp_filepath, wp_path)
		except (IOError, OSError) as e:
			log.error(str(e))
			raise GetImageError(str(e))

		return wp_path


	def save_image_info(self, source, wp_path, image):
		if image.db_image is None:
			db_image = Image()
		else:
			db_image = image.db_image

		db_image.type = image.type
		db_image.width = image.i_width
		db_image.height = image.i_height

		db_image.size = stat(wp_path).st_size

		db_image.filepath = wp_path
		db_image.time = int(time())

		if image.db_image is None:
			db_image.url = image.url

			db_image.title = image.title
			db_image.description = image.description[0: 1024] if image.description is not None else None
			db_image.context_url = image.context_url
			db_image.artist = image.user

			db_image.trace = source.get_trace()

		db_image.save()
		return db_image.id

