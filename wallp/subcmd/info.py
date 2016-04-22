from datetime import datetime
import os
import textwrap

from redlib.api.prnt import format_size
from redcmd.api import Subcommand, subcmd, CommandError

from ..db.app.images import Images as DBImages, DBImageError
from ..util.printer import printer


__all__ = ['InfoSubcommand']


class InfoSubcommand(Subcommand):

	@subcmd
	def info(self):
		'Print information about current wallpaper image.'
		self.print_info()

		
	def get_wallpaper_image(self):
		try:
			db_images = DBImages()
			image = db_images.get_current_wallpaper_image()
		except DBImageError as e:
			print(e)
			raise CommandError()
		return image


	def print_info(self):
		image = self.get_wallpaper_image()

		printer.printf('filepath', image.filepath)
		image.url and printer.printf('url', image.url)
		printer.printf('time', datetime.fromtimestamp(image.time).strftime('%d %b %Y, %I:%M:%S'))
		printer.printf('type', image.type)
		printer.printf('size', format_size(image.size))
		printer.printf('dimensions', str(image.width) + 'x' + str(image.height))
		image.artist and printer.printf('username', image.artist)
		image.title and printer.printf('title', image.title)
		image.description and printer.printf('description', image.description)
		image.context_url and printer.printf('context url', image.context_url)

		if len(image.trace) > 0:
			printer.printf('', '')
			printer.printf('trace')
			for step in image.trace:
				printer.printf(step.name, step.data)

