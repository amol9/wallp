import os

from mutils.system import *

from wallp.logger import log
from wallp.gnome_desktop import GnomeDesktop
from wallp.windows_desktop import WindowsDesktop
from wallp.kde_plasma_desktop import KdePlasmaDesktop
from wallp.linux_desktop_helper import uses_dbus


class DesktopException(Exception):
	pass


@uses_dbus
def get_desktop():
	if is_linux():
		gdmsession = os.environ.get('GDMSESSION', None)
		if gdmsession is None:
			log.error('could not read environment variable: GDMSESSION')
			raise DesktopException()

		if gdmsession.startswith('ubuntu') or gdmsession.startswith('gnome'):
			return GnomeDesktop()
		elif gdmsession == 'kde-plasma':
			return KdePlasmaDesktop()
		else:
			log.error('unsupported window manager: %s'%gdmsession)
	elif is_windows():
		return WindowsDesktop()
	else:
		log.error('unsupported OS')

	return None
