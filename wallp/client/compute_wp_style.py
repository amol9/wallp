
from mutils.image.imageinfo import get_image_info

from ..util.logger import log
from ..desktop.desktop_factory import get_desktop
from ..globals import Const


def compute_wp_style(wp_width, wp_height):
	assert type(wp_width) == int
	assert type(wp_height) == int

	dt = get_desktop()
	
	dt_width, dt_height = dt.get_size()
	log.debug('desktop: width=%d, height=%d'%(dt_width, dt_height))

	style = None
	buf = None

	log.debug('image: width=%d, height=%d'%(wp_width, wp_height))

	if wp_width < 5 and wp_height < 5:
		style = 'tiled'
	else:
		same_ar = False
		dt_ar = float(dt_width) / dt_height
		wp_ar = float(wp_width) / wp_height
		
		if abs(dt_ar - wp_ar) < 0.01:
			same_ar = True	

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

