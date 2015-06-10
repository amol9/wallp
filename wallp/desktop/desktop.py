from abc import ABCMeta, abstractmethod


class DesktopError(Exception):
	pass


class Desktop():
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_size(self):
		pass

	@abstractmethod
	def set_wallpaper(self, filepath, style=None):
		pass

	@abstractmethod
	def set_wallpaper_style(self, style):
		pass

