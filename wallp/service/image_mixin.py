
from .image_source import ImageSource


class ImageMixin(object):
	def __init__(self):
		self._image_source = ImageSource()
		self._image_trace = []

	def get_image_source(self):
		return self._image_source

	def get_image_trace(self):
		return self._image_trace

	image_source = property(get_image_source)
	image_trace = property(get_image_trace)


