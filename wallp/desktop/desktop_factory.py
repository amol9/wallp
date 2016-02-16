import os

from redlib.api.system import *

from ..util.logger import log
from . import Desktop
from .windows_desktop import WindowsDesktop
from .linux_desktop_helper import uses_dbus
from . import gnome_desktop


def load_optional_module(module, package=None, err_msg=None):
	import importlib
	try:
		importlib.import_module(module, package=package)
	except ImportError as e:
		log.debug(e)
		if err_msg is not None:
			log.debug(err_msg)

load_optional_module('.kde_plasma_desktop', package='wallp.desktop', err_msg='KDE Plasma will not be supported.')


@uses_dbus
def get_desktop():
	if is_linux():
		gdmsession = os.environ.get('GDMSESSION', None)
		if gdmsession is None:
			log.error('could not read environment variable: GDMSESSION')
			raise DesktopError()

		for desktop_class in Desktop.__subclasses__():
			if desktop_class.supports(gdmsession):
				return desktop_class()

		log.error('unsupported window manager: %s'%gdmsession)
		if gdmsession == 'kde-plasma':
			log.error('install dbus for python (python-dbus or python3-dbus) to support KDE Plasma')
	elif is_windows():
		return WindowsDesktop()
	else:
		log.error('unsupported OS')

	return None
