import shutil
import tempfile
from os.path import join as joinpath
from time import time
import os
import re
from datetime import datetime, timedelta

from mutils.system import get_pictures_dir, prints
from mutils.image.imageinfo import get_image_info

from ..service import service_factory, ServiceError, IHttpService, IImageGenService
from ..util.retry import Retry
from ..util.logger import log
from ..db import Image
from .. import web
from ..globals import Const
from ..desktop import desktop_factory, DesktopError
from .compute_wp_style import compute_wp_style
from ..server.protocol import WPState
from mayserver.transport.pipe_connection import PipeConnection
from ..db import func as dbfunc, GlobalVars


class GetImageError(Exception):
	pass


class ChangeWPError(Exception):
	pass


class KeepError(Exception):
	pass


class Client:
	def __init__(self, service_name=None, query=None, color=None, transport=None):
		self._service_name = service_name
		self._query = query
		self._color = color
		assert type(transport) == PipeConnection if transport is not None else True
		self._transport = transport


	def change_wallpaper(self):
		if self.keep_timeout_not_expired():
			return

		try:
			if self._transport is not None:
				self._transport.write_blocking(WPState.CHANGING)

			filepath, width, height, image_id = self.get_image()
			style = compute_style(width, height)

			dt = get_desktop()
			dt.set_wallpaper(filepath, style=style)

			globalvars = GlobalVars()
			globalvars.set('current_wallpaper_image', image_id)
			globalvars.set('last_change_time', int(time()))

			if self._transport is not None:
				self._transport.write_blocking(WPState.READY)
				self._transport.write_blocking(filepath)
		
		except DesktopError as e:
			log.error('error while changing wallpaper')

		except GetImageError as e:
			log.error('error while getting image for wallpaper')
			if self._transport is not None:
				self._transport.write_blocking(WPState.ERROR)
			raise ChangeWPError()

		if is_py3(): print('')


	def keep_timeout_not_expired(self):
		keep_timeout = GlobalVars().get('keep_timeout')
		if keep_timeout is not None and keep_timeout > time():
			expiry = datetime.fromtimestamp(keep_timeout).strftime('%d %b %Y, %H:%M:%S')
			log.error('current wallpaper is set not to change until %s'%expiry)
			return True
		return False


	def get_image(self):
		retry = Retry(retries=3, final_exc=GetImageError())

		while retry.left():
			service = self.get_service()
						
			try:
				temp_image_path, ext, image_url = self.get_image_to_temp_file(service, self._query, self._color)
				wp_path = self.move_temp_file(temp_image_path, ext)
				image_type, image_width, image_height = get_image_info(None, filepath=wp_path)
				image_id = self.save_image_info(service, wp_path, image_url, image_type, image_width, image_height)

				retry.cancel()

			except ServiceError as e:
				log.error('unable to get image from %s'%self._service_name)
				if self._service_name is not None:
					retry.cancel()
				else:
					retry.retry()
				raise GetImageError()

		return wp_path, image_width, image_height, image_id


	def get_service(self):
		if self._service_name == None:
			service = service_factory.get_random()
		else:
			service = service_factory.get(self._service_name)
			if service is None:
				log.error('%s: unknown service or service is disabled'%self._service_name)
				raise GetImageError()

		prints('[%s]'%self._service_name)
		log.debug('\nusing %s..'%self._service_name)

		return service


	def get_image_to_temp_file(self, service, query, color):
		image_url = None
		if IHttpService.providedBy(service):
			retry = Retry(retries=1, final_exc=ServiceError())
			while retry.left():
				f = None
				try:
					image_url = service.get_image_url(query=query, color=color)
						
					ext = image_url[image_url.rfind('.') + 1 : ]
					fn, temp_image_path = tempfile.mkstemp()
					f = os.fdopen(fn, 'r+b')

					web.func.download(image_url, open_file=f)
					retry.cancel()

				except web.exc.TimeoutError as e:
					log.error(str(e))
					retry.retry()

				except web.exc.DownloadError as e:
					log.error(str(e))
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

		image_source = service.image_source
		image.description = image_source.description
		image.artist = image.artist

		#self.add_trace(image.trace, service.image_trace)
		image.trace = service.image_trace

		image.save()
		return image.id


	def add_trace(self, trace_list, steps):
		step = 1
		for trace_step in steps:
			trace_step.step = 0
			trace_list.append(trace_step)
			step += 1


	def keep_wallpaper(self, period):
		period_map = { 's': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks' }
		period_regex = re.compile("(\d{1,3})((s|m|h|d|w|M|Y))")

		match = period_regex.match(period)
		
		if match is None:
			raise KeepError('bad time period: %s'%period)

		num = int(match.group(1))
		abbr_period = match.group(2)
		tdarg = {}	

		if abbr_period == 'M':
			tdarg['days'] = 30 * num
		elif abbr_period == 'Y':
			tdarg['days'] = 365 * num
		else:
			tdarg[period_map[abbr_period]] = num

		td = timedelta(**tdarg)
		keep_timeout = int(time()) + td.total_seconds()

		globalvars = GlobalVars()
		globalvars.set('keep_timeout', keep_timeout)

