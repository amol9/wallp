import ctypes

from wallp.desktop import Desktop
from mutils.system import *

if is_windows():
	if is_py3(): import winreg
	else: import _winreg as winreg


class WindowsDesktop(Desktop):
	wp_styles = {
		'none': '0',
		'tiled': '0',
		'centered': '0',
		'scaled': '6',
		'stretched': '2',
		'zoom': '10'
	}

	def get_size(self):
		user32 = ctypes.windll.user32
		width = user32.GetSystemMetrics(0)
		height = user32.GetSystemMetrics(1)		

		#log.debug('[desktop] width: ' + str(width) + ' height: ' + str(height))
		return width, height


	def set_wallpaper(self, filepath, style=None):
		if style is not None:
			self.set_wallpaper_style(style)

		user32 = ctypes.windll.user32

		SPIF_UPDATEINIFILE = 0x01
		SPIF_SENDCHANGE = 0x02			#???

		SPI_SETDESKWALLPAPER = 0x0014

		ret = user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 1, filepath, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
		

	def set_wallpaper_style(self, style):
		wp_style = self.wp_styles.get(style)
		if wp_style is None:
			wp_style = self.wp_styles['none']

		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Control Panel\\Desktop', 0, winreg.KEY_SET_VALUE)
		winreg.SetValueEx(key, 'WallpaperStyle', 0, winreg.REG_SZ, wp_style)

		if style == 'tiled':
			winreg.SetValueEx(key, 'TileWallpaper', 0, winreg.REG_SZ, '1')
		else:
			winreg.SetValueEx(key, 'TileWallpaper', 0, winreg.REG_SZ, '0')


