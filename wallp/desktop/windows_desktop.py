import ctypes

from redlib.api.system import *

from .wpstyle import WPStyle
from .desktop import Desktop, DesktopError


if is_windows():
	if is_py3(): import winreg
	else: import _winreg as winreg


class WindowsDesktop(Desktop):
	wp_styles = {
		WPStyle.NONE : 		'0',
		WPStyle.TILED : 	'0',
		WPStyle.CENTERED : 	'0',
		WPStyle.SCALED : 	'6',
		WPStyle.STRETCHED : 	'2',
		WPStyle.ZOOM : 		'10'
	}

	SPIF_UPDATEINIFILE 	= 0x01
	SPIF_SENDCHANGE 	= 0x02
	SPI_SETDESKWALLPAPER 	= 0x0014
	WM_SETTINGCHANGE 	= 0x1A
	HWND_BROADCAST 		= 0xFFFF
	SPI_GETDESKWALLPAPER 	= 0x0073

	user32 = ctypes.windll.user32
	max_path = 512

	@staticmethod
	def supports(gdmsession):
		return False


	def get_size(self):
		width = self.user32.GetSystemMetrics(0)
		height = self.user32.GetSystemMetrics(1)		

		return width, height


	def set_wallpaper(self, filepath, style=None):
		self.set_wallpaper_style(style)
		self.spi_set_wallpaper(filepath)


	def spi_set_wallpaper(self, filepath):
		self.user32.SystemParametersInfoW(self.SPI_SETDESKWALLPAPER, 1, filepath, self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE)
		

	def set_wallpaper_style(self, style):
		wp_style = None
		if style is None:
			wp_style = self.wp_styles.get(WPStyle.NONE)
		else:
			wp_style = self.wp_styles.get(int(style))

		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Control Panel\\Desktop', 0, winreg.KEY_SET_VALUE)
		winreg.SetValueEx(key, 'WallpaperStyle', 0, winreg.REG_SZ, wp_style)

		if int(style) == WPStyle.TILED:
			winreg.SetValueEx(key, 'TileWallpaper', 0, winreg.REG_SZ, '1')
		else:
			winreg.SetValueEx(key, 'TileWallpaper', 0, winreg.REG_SZ, '0')
		
		self.spi_set_wallpaper(self.get_wallpaper())	# have to set wallpaper again for style change to take effect


	def get_wallpaper(self):
		filepath_buffer = ctypes.create_unicode_buffer(self.max_path)
		self.user32.SystemParametersInfoW(self.SPI_GETDESKWALLPAPER, self.max_path, filepath_buffer, 0)

		return filepath_buffer.value


	def get_wallpaper_style(self):
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Control Panel\\Desktop', 0, winreg.KEY_QUERY_VALUE)
		tiled, _ = winreg.QueryValueEx(key, 'TileWallpaper')

		if tiled == '1':
			return WPStyle(WPStyle.TILED)
		else:
			style_val, _ = winreg.QueryValueEx(key, 'WallpaperStyle')
			style = dict([(v, k) for (k, v) in self.wp_styles.items()]).get(style_val, None)
			return WPStyle(style)

