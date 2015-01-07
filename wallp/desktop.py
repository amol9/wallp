import platform
from abc import ABCMeta, abstractmethod
import ctypes
from subprocess import call, check_output
import re

from wallp.system import *
from wallp.logger import log


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
	def get_size(self):
		xinfo = check_output(['xdpyinfo'])
		dim_regex = re.compile(".*dimensions:\s+(\d+)x(\d+).*", re.M | re.S)
		m = dim_regex.match(xinfo)

		if m:
			width = int(m.group(1))
			height = int(m.group(2))
			log.debug('[desktop] width: ' + str(width) + ' height: ' + str(height))

		return width, height

	
	def set_wallpaper(self, filepath):
		call(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', 'file://' + imagepath])


	def set_wallpaper_style(self, style):
		call(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-options', 'zoom'])



class WindowsDesktop(Desktop):
	def get_size(self):
		user32 = ctypes.windll.user32
		width = user32.GetSystemMetrics(0)
		height = user32.GetSystemMetrics(1)		

		log.debug('[desktop] width: ' + str(width) + ' height: ' + str(height))
		return width, height


	def set_wallpaper(self, filepath):
		user32 = ctypes.windll.user32

		SPIF_UPDATEINIFILE = 0x01
		SPIF_SENDCHANGE = 0x02			#???

		SPI_SETDESKWALLPAPER = 0x0014

		ret = user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 1, "c:\\Users\\amol\\Desktop\\SnowyStoat.jpg", SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
		

	def set_wallpaper_style(self, style):
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Control Panel\\Desktop', 0, winreg.KEY_SET_VALUE)
		winreg.SetValueEx(key, 'WallpaperStyle', 0, winreg.REG_SZ, "10")


def get_desktop():
	if is_linux(): return LinuxDesktop()
	elif is_windows(): return WindowsDesktop()
	else: log.error('unsupported OS')

	return None
