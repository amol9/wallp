from time import sleep

from redcmd.api import Subcommand, subcmd, Arg, CommandError, IntArg, FloatArg

from ...util.printer import printer
from ...wallpaper import Wallpaper, WallpaperError
from ... import const


class SourceSubcommand(Subcommand):

	def __init__(self):
		self._repeat_count = 1
		self._repeat_delay = 0.0


	def ignore_image_filter(self, ignore_image_filter=Arg(opt=True, default=False, short='iif', hidden=True)):
		'ignore_image_filter: ignore image filters such as size, dimensions, etc.'

		const.ignore_image_filter = ignore_image_filter


	def repeat(self, count=IntArg(opt=True, default=1, hidden=True, short='rptc', min=1, max=100),
			delay=FloatArg(opt=True, default=0, hidden=True, short='rptd', min=0.0)):

		self._repeat_count = count
		self._repeat_delay = delay



	def no_cache(self, no_cache=Arg(opt=True, default=False, short='noc', hidden=True)):
		
		const.cache_enabled = not no_cache


	def select(self, select=Arg(opt=True, default=False, short='noc', hidden=True)):
		pass


	@subcmd(add=[ignore_image_filter, repeat, no_cache], add_rec=True, add_skip=True)
	def source(self):
		'Select source for wallpaper.'
		pass


	def change_wallpaper(self, params):
		exc = None

		for _ in range(0, self._repeat_count):
			try:
				wallpaper = Wallpaper(params=params)
				wallpaper.change()
			except WallpaperError as e:
				printer.printf('error', str(e))
				exc = CommandError()

			sleep(self._repeat_delay)

		if exc is not None:
			raise exc

