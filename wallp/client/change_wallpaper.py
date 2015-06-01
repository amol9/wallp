
from mutils.system import *

from ..desktop import desktop_factory, DesktopException
from . import get_image, compute_style
from ..util import logger


class CWSpec:
	service_name 	= None
	query 		= None
	color 		= None
	transport 	= None


def change_wallpaper(spec):
	try:
		wp_path = get_image(spec)
		style = compute_style(wp_path)

		dt = get_desktop()
		dt.set_wallpaper(wp_path, style=style)

		if spec.transport is not None:
			#assert type
			#spec.transport.write()
	
	except DesktopException:
		log.error('error while changing wallpaper')

	if is_py3(): print('')

