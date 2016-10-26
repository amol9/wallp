import os

from redlib.api.system import sys_command, CronDBus, CronDBusError, is_linux, is_windows

from ..util.logger import log
from . import Desktop, DesktopError
from . import gnome_desktop
from . import feh_desktop
if is_windows():
	from .windows_desktop import WindowsDesktop


def load_optional_module(module, package=None, err_msg=None):
	import importlib
	try:
		importlib.import_module(module, package=package)
	except ImportError as e:
		print(e)
		if err_msg is not None:
			print(err_msg)

load_optional_module('.kde_plasma_desktop', package='wallp.desktop', err_msg='KDE Plasma will not be supported.')


def get_desktop():
	if is_linux():
		crondbus = CronDBus(vars=['GDMSESSION', 'DISPLAY', 'XDG_CURRENT_DESKTOP'])
		crondbus.setup()

		gdmsession = os.environ.get('GDMSESSION', None)
		xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', None)

		if gdmsession is None and xdg_current_desktop is None:
			log.error('could not read environment variables: GDMSESSION or XDG_CURRENT_DESKTOP')
			raise DesktopError()

		for desktop_class in Desktop.__subclasses__():
			if desktop_class.supports(gdmsession, xdg_current_desktop):
				return desktop_class()

		log.error('unsupported window manager: %s, %s'%(gdmsession, xdg_current_desktop))
	elif is_windows():
		return WindowsDesktop()
	else:
		log.error('unsupported OS')

	return None
