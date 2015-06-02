
from mutils.system import *

from ..desktop import desktop_factory, DesktopException
from . import get_image, compute_style
from ..util import logger
from ..server.protocol import WPState
from ..server.transport import PipeConnection


class CWSpec:
	service_name 	= None
	query 		= None
	color 		= None
	transport 	= None


def change_wallpaper(spec):
	assert type(spec.transport) == PipeConnection

	try:
		if spec.transport is not None:
			spec.transport.write_blocking(WPState.CHANGING)

		wp_path = get_image(spec)
		style = compute_style(wp_path)

		dt = get_desktop()
		dt.set_wallpaper(wp_path, style=style)

		if spec.transport is not None:
			spec.transport.write_blocking(WPState.READY)
	
	except DesktopException as e:
		log.error('error while changing wallpaper')

	except GetImageError as e
		log.error('error while getting image for wallpaper')
		if spec.transport is not None:
			spec.transport.write_blocking(WPState.ERROR)
		raise ChangeWPError()

	if is_py3(): print('')

