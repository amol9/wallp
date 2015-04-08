
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
