import shutil
from mutils.system import *

from ..service.bing import Bing
from ..util.logger import log
from ..service.imgur import Imgur
from ..service.google import Google
from ..service.reddit import Reddit
from ..service.bitmap import Bitmap
from ..service import service_factory, ServiceException
from ..desktop.desktop_factory import get_desktop
from ..util.imageinfo import get_image_info
from ..globals import Const


def get_image(service_name=None, query=None, color=None):
	service = None
	wp_path = None

	retry = 3
	while(retry > 0):
		if service_name == None:
			service = service_factory.get_random()
		else:
			service = service_factory.get(service_name)
			if service is None:
				log.info('unknown service or service is disabled')
				return
		prints('[%s]'%service.name)
		log.debug('[%s]'%service.name)
		#if log.to_stdout(): print('')
		
		try:
			temp_basename = 'wallp_temp'
			dirpath = get_pictures_dir() if not Const.debug else '.'
			
			tempname = service.get_image(dirpath, temp_basename, query=query, color=color)
			wp_path = joinpath(dirpath, Const.wallpaper_basename + tempname[tempname.rfind('.'):])
			shutil.move(joinpath(dirpath, tempname), wp_path)


			retry = 0
		except ServiceException:
			log.error('unable to change wallpaper')
			retry = 0 if service_name else retry - 1

	return wp_path


def compute_style(wp_path):
	if wp_path is None:
		return

	dt = get_desktop()
	
	dt_width, dt_height = dt.get_size()
	log.debug('desktop: width=%d, height=%d'%(dt_width, dt_height))

	style = None
	buf = None
	with open(wp_path, 'rb') as f:
		buf = f.read(10000)

	_, wp_width, wp_height = get_image_info(buf, filepath=wp_path)
	log.debug('image: width=%d, height=%d'%(wp_width, wp_height))

	if wp_width < 5 and wp_height < 5:
		style = 'tiled'
	else:
		same_ar = False
		dt_ar = float(dt_width) / dt_height
		wp_ar = float(wp_width) / wp_height
		
		if abs(dt_ar - wp_ar) < 0.01:
			same_ar = True	

		#import pdb; pdb.set_trace()		
		wr = float(wp_width) / dt_width
		hr = float(wp_height) / dt_height

		if (wr >= 0.9) and (hr >= 0.9):
			style = 'scaled' if same_ar else 'zoom'
		elif (wr < 0.9) or (hr < 0.9):
			style = 'centered'
		else:
			style = 'scaled' if same_ar else 'zoom' 

	log.debug('style: %s'%style)

	return style

