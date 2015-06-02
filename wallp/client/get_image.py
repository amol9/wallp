import shutil

from mutils.system import get_pictures_dir

from ..service import service_factory, ServiceException
from ..util.retry import Retry
from ..util.logger import log
from . import CWSpec


class GetImageError(Exception):
	pass


def get_image(spec):
	assert type(spec) == CWSpec

	service = None
	wp_path = None

	retry = Retry(retries=3, final_exc=GetImageError())

	while retry.left():
		if spec.service_name == None:
			service = service_factory.get_random()
		else:
			service = service_factory.get(spec.service_name)
			if service is None:
				log.info('unknown service or service is disabled')
				return

		prints('[%s]'%spec.service.name)
		log.debug('[%s]'%spec.service.name)
		#if log.to_stdout(): print('')
		
		try:
			temp_basename = 'wallp_temp'
			dirpath = get_pictures_dir() if not Const.debug else '.'
			
			tempname = service.get_image(dirpath, temp_basename, query=spec.query, color=spec.color)
			wp_path = joinpath(dirpath, Const.wallpaper_basename + tempname[tempname.rfind('.'):])
			shutil.move(joinpath(dirpath, tempname), wp_path)

		except ServiceException as e:
			log.error('unable to change wallpaper')
			if service_name is not None:
				retry.cancel()
			else:
				retry.retry()

	return wp_path

