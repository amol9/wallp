
from redlib.api.system import sys_command

from .desktop import Desktop
from .wpstyle import WPStyle
from ..util.logger import log
from .linux_desktop_helper import get_desktop_size, uses_dbus


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

	@uses_dbus
	def get_size(self):
		return get_desktop_size()

	
	@uses_dbus
	def set_wallpaper(self, filepath, style=None):
		cmd = 'gsettings set org.gnome.desktop.background picture-uri file://%s'%filepath
		sys_command(cmd)
		
		if style is not None:
			self.set_wallpaper_style(style)


	@uses_dbus
	def set_wallpaper_style(self, style):
		wp_style = self.wp_styles.get(style)
		if wp_style is None:
			wp_style = self.wp_styles['none']

		cmd = 'gsettings set org.gnome.desktop.background picture-options %s'%wp_style
		sys_command(cmd)

