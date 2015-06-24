from datetime import datetime
import os

from ..subcommand import Subcommand, subcmd
from ...db import func as dbfunc


class InfoSubcommand(Subcommand):

	@subcmd
	def info(self):
		'help: print information about current wallpaper image.'

		self.print_info()

		
	def get_image_info(self):
		image = dbfunc.get_current_wallpaper_image()
		return image


	def print_info(self):
		image = self.get_image_info()

		output = [
		('filepath', 	image.filepath),
		('url', 	image.url),
		('time', 	datetime.fromtimestamp(image.time).strftime('%d %b %Y, %I:%M:%S')),
		('type',	image.type),
		('artist',	image.artist) if image.artist is not None else (),
		('description',	image.description) if image.description is not None else (),
		('dimensions',	str(image.width) + 'x' + str(image.height)),
		('size',	self.sizefmt(image.size)),
		('score',	str(image.score))
		]

		for name, data in [(p[0], p[1]) for p in output if len(p) == 2]:
			print("{0:<20}: {1}".format(name, data))

		if len(image.trace) > 0:
			print('\ntrace:')

			for item in image.trace:
				line = str(item.step) + '. '
				line += "{0:<25}".format(item.name)
				if item.data is not None:
					line += ': ' + item.data
				print(line)

		print('')


	def sizefmt(self, num, suffix='B'):
		'''source: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
			by: Sridhar Ratnakumar'''

		for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
			if abs(num) < 1024.0:
				return "%3.1f%s%s" % (num, unit, suffix)
			num /= 1024.0

		return "%.1f%s%s" % (num, 'Yi', suffix)
