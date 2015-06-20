
from .image_source import ImageSource
from ..db import ImageTrace


class ImageInfoMixin(object):
	def __init__(self):
		super(ImageInfoMixin, self).__init__()
		self._image_source = ImageSource()
		self._image_trace = []
		self._step = 1


	def add_trace_step(self, name, data):
		self._image_trace.append(ImageTrace(step=self._step, name=name, data=data))
		self._step += 1


	def get_image_source(self):
		return self._image_source


	def get_image_trace(self):
		return self._image_trace


	image_source = property(get_image_source)
	image_trace = property(get_image_trace)

