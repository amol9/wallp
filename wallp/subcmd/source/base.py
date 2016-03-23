
from redcmd.api import Subcommand, subcmd, Arg, CommandError

from ...util.printer import printer
from ...wallpaper import Wallpaper, WallpaperError


class SourceSubcommand(Subcommand):

	@subcmd
	def source(self):
		'Select source for wallpaper.'
		pass


	def change_wallpaper(self, params):
		try:
			wallpaper = Wallpaper(params=params)
			wallpaper.change()
		except WallpaperError as e:
			printer.printf('error', str(e))
			raise CommandError()


