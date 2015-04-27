
from wallp.desktop import Desktop
from wallp.logger import log
from wallp.command import command
from wallp.config import config
from wallp.linux_desktop_helper import get_desktop_size, uses_dbus


class GnomeDesktop(Desktop):
	wp_styles = {
		'none': 'none',
		'tiled': 'wallpaper',
		'centered': 'centered',
		'scaled': 'scaled',
		'stretched': 'strecthed',
		'zoom': 'zoom'
	}


	@uses_dbus
	def get_size(self):
		return get_desktop_size()

	
	@uses_dbus
	def set_wallpaper(self, filepath, style=None):
		cmd = 'gsettings set org.gnome.desktop.background picture-uri file://%s'%filepath
		with command(cmd) as c:
			c.execute()
		
		if style is not None:
			self.set_wallpaper_style(style)


	@uses_dbus
	def set_wallpaper_style(self, style):
		wp_style = self.wp_styles.get(style)
		if wp_style is None:
			wp_style = self.wp_styles['none']

		cmd = 'gsettings set org.gnome.desktop.background picture-options %s'%wp_style
		with command(cmd) as c:
			c.execute()

