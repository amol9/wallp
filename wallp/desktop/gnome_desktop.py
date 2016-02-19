
from redlib.api.system import sys_command, CronDBus, CronDBusError

from .desktop import Desktop, DesktopError
from .wpstyle import WPStyle
from ..util.logger import log
from .linux_desktop_helper import get_desktop_size


class GnomeDesktop(Desktop):
	wp_styles = {
		WPStyle.NONE : 		'none',
		WPStyle.TILED : 	'wallpaper',
		WPStyle.CENTERED : 	'centered',
		WPStyle.SCALED : 	'scaled',
		WPStyle.STRETCHED : 	'strecthed',
		WPStyle.ZOOM : 		'zoom'
	}

	@staticmethod
	def supports(gdmsession):
		return gdmsession.startswith('ubuntu') or gdmsession.startswith('gnome')

	def __init__(self):
		self._crondbus = CronDBus(vars=['GDMSESSION', 'DISPLAY'])
		self._crondbus.setup()


	def __del__(self):
		self._crondbus.remove()


	def get_size(self):
		return get_desktop_size()

	
	def set_wallpaper(self, filepath, style=None):
		cmd = 'gsettings set org.gnome.desktop.background picture-uri file://%s'%filepath
		sys_command(cmd)
		
		if style is not None:
			self.set_wallpaper_style(style)


	def set_wallpaper_style(self, style):
		wp_style = self.wp_styles.get(int(style))
		if wp_style is None:
			wp_style = self.wp_styles['none']

		cmd = 'gsettings set org.gnome.desktop.background picture-options %s'%wp_style
		sys_command(cmd)


	def get_wallpaper(self):
		cmd = 'gsettings get org.gnome.desktop.background picture-uri'
		_, op = sys_command(cmd)
		filepath_prefix = 'file://'

		if not op[1:].startswith(filepath_prefix):
			raise DesktopError('wallpaper path probably not a local file path: %s'%op)

		return op.strip()[len(filepath_prefix) + 1 : -1]
	
	
	def get_wallpaper_style(self):
		cmd = 'gsettings get org.gnome.desktop.background picture-options'
		_, op = sys_command(cmd)

		style_name = op.strip()[1 : -1]
		style = dict([(v, k) for (k, v) in self.wp_styles.items()]).get(style_name, None)

		return WPStyle(style)
		


