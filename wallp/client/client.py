import shutil
import tempfile
from os.path import join as joinpath, exists
from time import time
import os
import re
from datetime import datetime, timedelta

from redlib.api.system import *
from redlib.api.image import get_image_info
from redlib.api.prnt import prints, format_size

from ..service import ServiceFactory, ServiceDisabled, NoEnabledServices, ServiceError, IHttpService, IImageGenService
from ..util.retry import Retry
from ..util.logger import log
from ..db import Image, Config
from ..web.func import get, HttpError
from ..globals import Const
from ..desktop import desktop_factory, DesktopError, get_desktop
from ..desktop.wpstyle import WPStyle, compute_style
from ..server.protocol import WPState
from mayloop.transport.pipe_connection import PipeConnection
from ..db import func as dbfunc, GlobalVars, VarError
from ..util.printer import printer


class GetImageError(Exception):
	pass


class ChangeWPError(Exception):
	pass


class KeepError(Exception):
	pass


class Client:
	def __init__(self, service_name=None, query=None, color=None, transport=None, service_params=None):
		self._service_name = service_name
		self._query = query
		self._color = color
		assert type(transport) == PipeConnection if transport is not None else True
		self._transport = transport
		self._service_params = service_params


	def change_wallpaper(self):
		if self.keep_timeout_not_expired():
			return

		try:
			if self._transport is not None:
				self._transport.write_blocking(WPState.CHANGING)

			filepath, im_width, im_height, image_id = self.get_image()

			dt = get_desktop()
			wp_style = compute_style(im_width, im_height, *dt.get_size())

			dt.set_wallpaper(filepath, style=wp_style)
			printer.printf('wallpaper changed', '', verbosity=2)

			globalvars = GlobalVars()
			try:
				globalvars.set('current_wallpaper_image', image_id)
				globalvars.set('last_change_time', int(time()))
			except VarError as e:
				log.error(str(e))

			if self._transport is not None:
				self._transport.write_blocking(WPState.READY)
				self._transport.write_blocking(filepath)
		
		except DesktopError as e:
			log.error('error while changing wallpaper')

		except GetImageError as e:
			log.error(str(e))
			if self._transport is not None:
				self._transport.write_blocking(WPState.ERROR)
			raise ChangeWPError()

		if is_py3(): print('')


	def keep_timeout_not_expired(self):
		try:
			keep_timeout = GlobalVars().get('keep_timeout')
		except VarError as e:
			log.error(str(e))
			return None
			#return False

		if keep_timeout is not None and keep_timeout > time():
			expiry = datetime.fromtimestamp(keep_timeout).strftime('%d %b %Y, %H:%M:%S')
			log.error('current wallpaper is set not to change until %s'%expiry)
			return True
		return False


	def get_image(self):
		retry = Retry(retries=3, final_exc=GetImageError())

		while retry.left():
			try:
				service = self.get_service()
				temp_image_path, ext, image_url = self.get_image_to_temp_file(service, self._query, self._color, self._service_params)
				wp_path = self.move_temp_file(temp_image_path, ext)
				image_type, image_width, image_height = get_image_info(None, filepath=wp_path)
				image_id = self.save_image_info(service, wp_path, image_url, image_type, image_width, image_height)

				retry.cancel()

			except ServiceError as e:
				log.error(e)
				printer.printf('error', str(e))

				if self._service_name is not None:
					retry.cancel()
				else:
					retry.retry()
				raise GetImageError()

		return wp_path, image_width, image_height, image_id


	def get_service(self):
		if self._service_name == None:
			try:
				service = ServiceFactory().get_random()
				printer.printf('selected random source', service.name)
			except NoEnabledServices as e:
				raise GetImageError('all services disabled')
		else:
			try:
				service = ServiceFactory().get(self._service_name)
				printer.printf('selected source', service.name)
			except ServiceDisabled as e:
				log.error('%s is disabled'%self._service_name)
				raise GetImageError()

			if service is None:
				log.error('%s: unknown service or service is disabled'%self._service_name)
				raise GetImageError()

		log.debug('\nusing %s..'%service.name)

		return service


	def get_image_to_temp_file(self, service, query, color, service_params):
		image_url = None
		if IHttpService.providedBy(service):
			retry = Retry(retries=3, final_exc=ServiceError())
			while retry.left():
				f = None
				try:
					if service_params is not None:
						image_url = service.get_image_url(query=query, color=color, params=service_params)
					else:
						image_url = service.get_image_url(query=query, color=color)
					
					if image_url is None:
						raise ServiceError()

					ext = image_url[image_url.rfind('.') + 1 : ]
					fn, temp_image_path = tempfile.mkstemp()
					f = os.fdopen(fn, 'r+b')

					get(image_url, open_file=f, msg='getting image', max_content_length=Config().get('image.max_size'))
					retry.cancel()

				except HttpError as e:
					log.error(e)
					printer.printf('error', str(e))
					retry.retry()

				finally:
					if f is not None:
						f.close()

		elif IImageGenService.providedBy(service):
			temp_image_path = service.get_image(query=query, color=color)
			ext = service.get_extension()

		return temp_image_path, ext, image_url


	def move_temp_file(self, temp_path, ext):
		dirpath = get_pictures_dir() if not Const.debug else '.'
		wp_path = joinpath(dirpath, Const.wallpaper_basename + '.' + ext)

		try:
			shutil.move(temp_path, wp_path)
		except IOError as e:
			#handle move error, write to temp file error, disk full?
			log.error(str(e))
			raise GetImageError()

		return wp_path


	def save_image_info(self, service, wp_path, image_url, image_type, image_width, image_height):
		image = Image()

		image.url = image_url
		image.filepath = wp_path
		image.time = int(time())

		image.type = image_type
		image.width = image_width
		image.height = image_height

		image.size = os.stat(wp_path).st_size

		image_context = service.image_context
		image.title = image_context.title
		image.description = image_context.description[0: 1024] if image_context.description is not None else None
		image.context_url = image_context.url
		image.artist = image_context.artist

		image.trace = service.image_trace

		image.save()
		return image.id

