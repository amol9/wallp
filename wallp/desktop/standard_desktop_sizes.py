import sys


class DesktopSizeException(Exception):
	pass


class StandardDesktopSizes():
	sizes = [
		(800, 600),
		(1024, 768),
		(1280, 800),
		(1280, 1024),
		(1366, 768),
		(1440, 900),
		(1600, 900),
		(1680, 1050),
		(1920, 1080),
		(1920, 1200)
	]


	def __contains__(self, size):
		return size in self.sizes


	def nearest(self, width, height):
		nwidth = min(self.sizes, key=lambda p: abs(width - p[0]))[0]
		nheight = min([(x, y) for (x, y) in self.sizes if x == nwidth], key=lambda p: abs(height - p[1]))[1]

		return (nwidth, nheight)


	def nearest_larger(self, width, height):
		nwidth = min(self.sizes, key=lambda p: sys.maxsize if p[0] < width else abs(width - p[0]))[0]
		
		if nwidth < width:
			raise DesktopSizeException('no standard size larger than width %d'%width)

		nheight = min([(x, y) for (x, y) in self.sizes if x == nwidth], key=lambda p: abs(height - p[1]))[1]

		return (nwidth, nheight)


def get_standard_desktop_size(width, height):
	std_sizes = StandardDesktopSizes()

	if (width, height) in std_sizes:
		return width, height

	try:
		return std_sizes.nearest_larger(width, height)
	except DesktopSizeException:
		return std_sizes.nearest(width, height)
	
