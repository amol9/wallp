import platform
from abc import ABCMeta, abstractmethod
import ctypes
import re

from wallp.system import *
from wallp.logger import log
from wallp.command import command


if is_windows():
	if is_py3(): import winreg
	else: import _winreg as winreg


class Desktop():
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_size(self):
		pass

	@abstractmethod
	def set_wallpaper(self, filepath):
		pass

	@abstractmethod
	def set_wallpaper_style(self, style):
		pass


class LinuxDesktop(Desktop):
	wp_styles = {
		'none': 'none',
		'tiled': 'wallpaper',
		'centered': 'centered',
		'scaled': 'scaled',
		'stretched': 'strecthed',
		'zoom': 'zoom'
	}


	def get_size(self):
		xinfo = None
		with command('xdpyinfo') as c:
			xinfo = c.execute()

		dim_regex = re.compile(".*dimensions:\s+(\d+)x(\d+).*", re.M | re.S)
		m = dim_regex.match(xinfo)

		if m:
			width = int(m.group(1))
			height = int(m.group(2))
			#log.debug('[desktop] width: ' + str(width) + ' height: ' + str(height))

		return width, height

	
	def set_wallpaper(self, filepath):
		cmd = 'gsettings set org.gnome.desktop.background picture-uri file://%s'%filepath
		with command(cmd) as c:
			c.execute()


	def set_wallpaper_style(self, style):
		wp_style = self.wp_styles.get(style)
		if wp_style is None:
			wp_style = self.wp_styles['none']

		cmd = 'gsettings set org.gnome.desktop.background picture-options %s'%wp_style
		with command(cmd) as c:
			c.execute()


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


	def set_wallpaper(self, filepath):
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


def get_desktop():
	if is_linux(): return LinuxDesktop()
	elif is_windows(): return WindowsDesktop()
	else: log.error('unsupported OS')

	return None
