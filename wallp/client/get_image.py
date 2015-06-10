import shutil
import tempfile
from os.path import join as joinpath
from time import time
import os

from mutils.system import get_pictures_dir, prints
from mutils.image.imageinfo import get_image_info

from ..service import service_factory, ServiceError, IHttpService, IImageGenService
from ..util.retry import Retry
from ..util.logger import log
from .cwspec import CWSpec
from ..db import Image
from .. import web
from ..globals import Const


class GetImageError(Exception):
	pass


def get_image(spec):
	assert spec.__class__ == CWSpec

	service = None
	wp_path = None
	image = Image()

	retry = Retry(retries=3, final_exc=GetImageError())

	while retry.left():
		if spec.service_name == None:
			service = service_factory.get_random()
		else:
			service = service_factory.get(spec.service_name)
			if service is None:
				log.info('unknown service or service is disabled')
				return

		prints('[%s]'%spec.service_name)
		log.debug('[%s]'%spec.service_name)
		#if log.to_stdout(): print('')
		
		try:
			temp_image_path = None
			if IHttpService.providedBy(service):
				image.url = service.get_image_url(query=spec.query, color=spec.color)
				
				ext = image.url[image.url.rfind('.') + 1 : ]
				fn, temp_image_path = tempfile.mkstemp()
				f = os.fdopen(fn, 'r+b')
				#save_path = temp_image_file.file#joinpath(pictures_dir, basename + '.' + ext)

				web.func.download(image.url, open_file=f)
				f.close()

			elif IImageGenService.providedBy(service):
				temp_image_path = service.get_image()
				ext = 'bmp'
			
			dirpath = get_pictures_dir() if not Const.debug else '.'
			wp_path = joinpath(dirpath, Const.wallpaper_basename + '.' + ext)

			shutil.move(temp_image_path, wp_path)

			image.filepath = wp_path
			image.time = int(time())

			image.type, image.width, image.height = get_image_info(None, filepath=wp_path)
			image.size = os.stat(wp_path).st_size

			image_source = service.image_source
			image.description = image_source.description
			image.artist = image.artist

			add_trace(image.trace, service.image_trace)

			image.save()
			retry.cancel()

		#except IOError as e:
			#handle move error, write to temp file error, disk full?
			#log.error(str(e))
			#import pdb; pdb.set_trace()

		except web.exc.TimeoutError as e:
			log.error(str(e))

		except web.exc.DownloadError as e:
			log.error(str(e))

		except ServiceError as e:
			log.error('unable to get image from %s'%spec.service_name)
			if spec.service_name is not None:
				retry.cancel()
			else:
				retry.retry()
			raise GetImageError()

	return wp_path, image.width, image.height



def add_trace(trace_list, steps):
	step = 1
	for trace_step in steps:
		trace_step.step = 0
		trace_list.append(trace_step)
		step += 1
