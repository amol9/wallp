
from redcmd.api import Subcommand, subcmd, Arg, CommandError
from redlib.api.image import get_image_info

from ..util import log
from ..desktop.wpstyle import WPStyle, compute_style, WPStyleError
from ..desktop.desktop_factory import get_desktop
from ..desktop.desktop import Desktop, DesktopError


__all__ = ['StyleSubcommand']


class StyleSubcommand(Subcommand):

	@subcmd
	def style(self):
		'Commands to get/set/compute wallpaper style.'
		pass


class StyleSubSubcommands(StyleSubcommand):

	def __init__(self):
		self._desktop = None


	@subcmd
	def set(self, style=Arg(choices=WPStyle.strings)):
		'''Change wallpaper style.
		style: 	wallpaper style name'''

		self.exc_desktop_call('set_wallpaper_style', WPStyle(style))


	@subcmd
	def get(self):
		'Get wallpaper style.'

		style = self.exc_desktop_call('get_wallpaper_style')
		print(style)


	@subcmd
	def auto(self):
		'Compute and set wallpaper style automatically.'

		filepath = self.exc_desktop_call('get_wallpaper')
		_, im_width, im_height = get_image_info(None, filepath=filepath)
		dt_width, dt_height = self.exc_desktop_call('get_size')

		wp_style = compute_style(im_width, im_height, dt_width, dt_height)
		self.exc_desktop_call('set_wallpaper_style', wp_style)
		
		print('wallpaper style set to: %s'%wp_style)


	def exc_desktop_call(self, meth, *args, **kwargs):
		if self._desktop is None:
			self._desktop = get_desktop()

		try:
			m = getattr(self._desktop.__class__, meth, None)
			if m is None:
				print('method %s not found in class %s'%(meth, self._desktop.__class__.__name__))
				raise CommandError()

			return m(self._desktop, *args, **kwargs)
		except (WPStyleError, DesktopError) as e:
			print(e)
			raise CommandError()

