from abc import ABCMeta, abstractmethod


class DesktopError(Exception):
	pass


class Desktop():
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_size(self):
		'Get desktop size.'
		pass

	@abstractmethod
	def set_wallpaper(self, filepath, style=None):
		'Set desktop wallpaper.'
		pass

	@abstractmethod
	def set_wallpaper_style(self, style):
		'Set wallpaper style.'
		pass

	@abstractmethod
	def get_wallpaper(self):
		'Get desktop wallpaper filepath.'
		pass

	@abstractmethod
	def get_wallpaper_style(self):
		'Get wallpaper style.'
		pass

