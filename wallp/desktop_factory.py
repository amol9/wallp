import os

from mangoutils.system import *

from wallp.logger import log
from wallp.gnome_desktop import GnomeDesktop
from wallp.windows_desktop import WindowsDesktop
from wallp.kde_plasma_desktop import KdePlasmaDesktop


def get_desktop():
	if is_linux():
		gdmsession = os.environ['GDMSESSION']
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
