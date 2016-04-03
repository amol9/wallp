
from ..db.app.config import Config
from ..desktop.desktop_factory import get_desktop
from .. import const


class ImageFilter:

	def __init__(self, min_width=None, min_height=None, max_width=None, max_height=None, max_size=None):
		config = Config()
		
		min_ratio = config.eget('image.min_ratio_to_desktop', default=const.min_ratio_to_desktop)
		max_ratio = config.eget('image.max_ratio_to_desktop', default=const.max_ratio_to_desktop)

		dt = get_desktop()
		dw, dh = dt.get_size()

		self.min_width	= min_width 	or int(dw * min_ratio)
		self.min_height	= min_height 	or int(dh * min_ratio)
		self.max_width	= max_width 	or int(dw * max_ratio)
		self.max_height	= max_height 	or int(dh * max_ratio)

		self.max_size	= max_size or config.eget('image.max_size', default=const.max_image_size)

		self.allow_seen_images = False

		self.ext_filters = []


	def match(self, image):
		result = True

		if const.ignore_image_filter:
			return True

		if result and image.width is not None:
			if self.min_width is not None and image.width < self.min_width:
				result = False
			if result and self.max_width is not None and image.width > self.max_width:
				result = False

		if result and image.height is not None:
			if self.min_height is not None and image.height < self.min_height:
				result = False
			if result and self.max_height is not None and image.height > self.max_height:
				result = False

		if result and image.size is not None:
			if self.max_size is not None and image.size > self.max_size:
				result = False

		if result and len(self.ext_filters) > 0:
			result = all(map(lambda f : f(image), self.ext_filters))

		return result


	def add_ext_filter(self, filter):
		self.ext_filters.append(filter)

