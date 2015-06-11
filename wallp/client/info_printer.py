from datetime import datetime


from ..db import func as dbfunc


class InfoPrinter:
	def __init__(self, filename):
		self._filename = filename


	def get_image_info(self):
		image = dbfunc.get_current_wallpaper_image()
		return image


	def print_info(self):
		image = self.get_image_info()

		output = \
		'filepath: ' + image.filepath + os.linesep + \
		'url: ' + image.url + os.linesep + \
		'time: ' + datetime.fromtimestamp(image.time).strftime('%d %b %Y, %I:%M:%S') + \
		'type: ' + image.type + os.linesep + \
		'artist: ' + image.artist + os.linesep if image.artist is not None else '' + \
		'description: ' + image.description + os.linesep if image.description is not None else '' + \
		'dimensions: ' + str(image.width) + 'x' + str(image.height) + os.linesep + \
		'size: ' + str(image.size) + os.linesep + \
		'score: ' + str(image.score) + os.linesep + \
		'trace:' + os.linesep
		for item in image.trace:
			output += item.name + (': ' + item.data if item.data is not None else '') + os.linesep

		print(output)

