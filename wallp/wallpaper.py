import shutil
import tempfile
from os.path import join as joinpath, exists
from time import time
from datetime import datetime, timedelta

from redlib.api.system import *
from mayloop.transport.pipe_connection import PipeConnection

from .util.retry import Retry
from .util.logger import log
from .db.model.image import Image
from . import const
from .desktop import DesktopError, get_desktop
from .desktop.wpstyle import WPStyle, compute_style
from .server.protocol import WPState
from .db.app.vars import Vars, VarError
from .db.app.images import Images as DBImages
from .util.printer import printer
from .source.source_factory import SourceFactory, SourceFactoryError
from .source.base import SourceError, SourceParams


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

			image_id = DBImages().save_image(source, wp_image_path, image)
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
			keep_timeout = Vars().eget('keep_timeout', default=None)
		except VarError as e:
			log.error(str(e))
			keep_timeout = None

		if keep_timeout is not None and keep_timeout > time():
			expiry = datetime.fromtimestamp(keep_timeout).strftime('%d %b %Y, %H:%M:%S')
			msg = 'current wallpaper is set not to change until %s'%expiry
			log.error(msg)
			raise WallpaperError(msg)


	def update_global_vars(self, image_id):
		vars = Vars()
		try:
			vars.eset('current_wallpaper_image', image_id)
			vars.eset('last_change_time', int(time()))
		except VarError as e:
			log.error(str(e))


	def get_image(self):
		retry = Retry(retries=3, final_exc=GetImageError())
		
		random_source = self._params.name is None
		while retry.left():
			try:
				source = self.get_source()
				params = source.params_cls() if random_source else self._params

				image = source.get_image(params=params)
				retry.cancel()

			except SourceError as e:
				log.error(e)

				if not random_source:
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
			log.info('source: %s'%source.name)
			return source
		except SourceFactoryError as e:
			log.error(e)
			raise WallpaperError(str(e))


	def move_temp_file(self, image):
		if image.filepath is not None:
			return image.filepath

		dirpath = get_pictures_dir() if not const.debug else '.'
		wp_path = joinpath(dirpath, const.wallpaper_basename + '.' + image.ext)

		try:
			shutil.move(image.temp_filepath, wp_path)
		except (IOError, OSError) as e:
			log.error(str(e))
			raise GetImageError(str(e))

		return wp_path

