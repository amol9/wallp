import os

from redlib.api.system import sys_command, CronDBus, CronDBusError, is_linux, is_windows

from ..util.logger import log
from . import Desktop
from . import gnome_desktop
if is_windows():
	from .windows_desktop import WindowsDesktop


def load_optional_module(module, package=None, err_msg=None):
	import importlib
	try:
		importlib.import_module(module, package=package)
	except ImportError as e:
		log.debug(e)
		if err_msg is not None:
			log.debug(err_msg)

load_optional_module('.kde_plasma_desktop', package='wallp.desktop', err_msg='KDE Plasma will not be supported.')


def get_desktop():
	if is_linux():
		crondbus = CronDBus(vars=['GDMSESSION', 'DISPLAY'])
		crondbus.setup()

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
