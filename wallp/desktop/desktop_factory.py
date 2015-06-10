import os

from mutils.system import *

from ..util.logger import log
from .gnome_desktop import GnomeDesktop
from .windows_desktop import WindowsDesktop
from .kde_plasma_desktop import KdePlasmaDesktop
from .linux_desktop_helper import uses_dbus


@uses_dbus
def get_desktop():
	if is_linux():
		gdmsession = os.environ.get('GDMSESSION', None)
		if gdmsession is None:
			log.error('could not read environment variable: GDMSESSION')
			raise DesktopError()

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
