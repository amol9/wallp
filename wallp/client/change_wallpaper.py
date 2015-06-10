
from mutils.system import *

from ..desktop import desktop_factory, DesktopError
from .get_image import get_image
from .compute_wp_style import compute_wp_style
from ..util import logger
from ..server.protocol import WPState
from mayserver.transport.pipe_connection import PipeConnection
from ..db import func
from .cwspec import CWSpec


def change_wallpaper(spec):
	assert type(spec) == CWSpec
	assert type(spec.transport) == PipeConnection

	try:
		if spec.transport is not None:
			spec.transport.write_blocking(WPState.CHANGING)

		filepath, width, height = get_image(spec)
		style = compute_style(widht, height)

		dt = get_desktop()
		dt.set_wallpaper(filepath, style=style)

		func.set_last_change_time()

		if spec.transport is not None:
			spec.transport.write_blocking(WPState.READY)
			spec.transport.write_blocking(filepath)
	
	except DesktopError as e:
		log.error('error while changing wallpaper')

	except GetImageError as e:
		log.error('error while getting image for wallpaper')
		if spec.transport is not None:
			spec.transport.write_blocking(WPState.ERROR)
		raise ChangeWPError()

	if is_py3(): print('')

