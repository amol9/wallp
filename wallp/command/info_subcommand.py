from datetime import datetime
import os
import textwrap

from redlib.api.system import get_terminal_size
from redcmd.api import Subcommand, subcmd, CommandError

from ..db import func as dbfunc
from ..db.exc import NotFoundError


class InfoSubcommand(Subcommand):

	@subcmd
	def info(self):
		'Print information about current wallpaper image.'

		self.print_info()

		
	def get_image_info(self):
		try:
			image = dbfunc.get_current_wallpaper_image()
		except NotFoundError as e:
			print(None)
			raise CommandError()
		return image


	def print_info(self):
		image = self.get_image_info()
		col1 = 20
		col2 = get_terminal_size()[0] - col1 - 3

		def wrap(text):
			lines = []
			for newline in text.split('\n'):
				lines += textwrap.wrap(newline, col2)
			return lines

		desc = (image.title if image.title is not None else '') + '\n' + \
			(image.description if image.description is not None else '')

		output = [
		('filepath', 	image.filepath),
		('url', 	image.url),
		('time', 	datetime.fromtimestamp(image.time).strftime('%d %b %Y, %I:%M:%S')),
		('type',	image.type),
		('size',	self.sizefmt(image.size)),
		('dimensions',	str(image.width) + 'x' + str(image.height)),
		('score',	str(image.score)),
		('artist',	image.artist) if image.artist is not None else (),
		('description',	wrap(desc)) if len(desc.strip()) > 0 else (),
		('context url', image.context_url) if image.context_url is not None else (),
		]

		for name, data in [(p[0], p[1]) for p in output if len(p) == 2]:
			if type(data) != list:
				lines = [data]
			else:
				lines = data
			for line in lines:
				print("{0:<20}{1} {2}".format(name, ':' if name != '' else ' ', line))
				name = ''

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

