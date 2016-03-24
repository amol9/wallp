from struct import pack
from random import choice
import tempfile
import os
from time import time

from redlib.api.colors import colorlist

from ..util.logger import log
from .base import SourceError, SourceParams, SourceResponse
from .base_source import BaseSource


class BitmapParams(SourceParams):
	name = 'bitmap'

	def __init__(self, color=None, width=None, height=None):
		self.color = color


class Bitmap(BaseSource):
	name = 'bitmap'

	def __init__(self, use_color_table=True):
		super(Bitmap, self).__init__()


	def get_extension(self):
		return 'bmp'


	def get_image(self, params=None):
		width, height = 2, 2

		color = params.color

		if color is not None:
			self.add_trace_step('color', color)
			if not color.startswith('0x'):
				c = colorlist.get(color)
				if c is None:
					raise SourceError('no such color')
				color = c

		else:
			color = choice(list(colorlist.keys()))
			self.add_trace_step('random color', color)
			color = colorlist[color]

		
		start_time = time()

		fn, temp_file_path = tempfile.mkstemp()
		f = os.fdopen(fn, 'wb')
		try:
			pa_size, _ = self.get_pixel_array_size(width, height)
			self.write_bmp_header(f, pa_size)
			self.write_dib_header(f, width, height)
			self.write_pixel_array(f, width, height, color)
		except IOError as e:
			log.error(str(e))
			raise SourceError()

		f.close()

		end_time = time()

		self.add_trace_step('generated bitmap', '%.3fms'%((end_time - start_time) * 1000))

		r = SourceResponse()
		r.im_type, r.im_width, r.im_height = self.get_image_info(temp_file_path)
		r.temp_filepath, r.ext = temp_file_path, 'bmp'
		return r


	def write_bmp_header(self, bmpfile, pa_size):
		bmpfile.write(b'BM')			#ID
		bmpfile.write(pack('i', 54 + pa_size))	#size
		bmpfile.write(pack('i', 0))		#unused
		bmpfile.write(pack('i', 54))		#offset for pixel array


	def write_dib_header(self, bmpfile, width, height):
		bmpfile.write(pack('i', 40))		#DIB header size
		bmpfile.write(pack('i', width))		#width of bitmap
		bmpfile.write(pack('i', height))	#height of bitmap
		bmpfile.write(pack('h', 1))		#no. of color planes
		bmpfile.write(pack('h', 24))		#no. of bits/pixel
		bmpfile.write(pack('i', 0))		#BI_RGB
		pa_size, _ = self.get_pixel_array_size(width, height)
		bmpfile.write(pack('i', pa_size))	#size of raw bitmap data
		bmpfile.write(pack('i', 2835))		#72dpi
		bmpfile.write(pack('i', 2835))		#72dpi
		bmpfile.write(pack('i', 0))		#no. of colors in the palette
		bmpfile.write(pack('i', 0))		#all colors are important

	
	def write_pixel_array(self, bmpfile, width, height, color):
		_, row_size = self.get_pixel_array_size(width, height)
		pixels_per_row = int(row_size / 3)
		pad_bytes = row_size - (pixels_per_row * 3)

		hex_color = int(color, 16)
		red = hex_color >> 16
		green = hex_color >> 8 & 0x00FF
		blue = hex_color & 0x0000FF

		for p in range(0, width * height, pixels_per_row):
			for i in range(pixels_per_row):
				bmpfile.write(pack('BBB', blue, green, red))
			for i in range(pad_bytes):
				bmpfile.write(pack('B', 0x00))
			


	def get_pixel_array_size(self, width, height):
		row_size = int((width * 24 + 31) / 32) * 4
		log.debug('row size: %d'%row_size)
		pa_size = row_size * height
		return pa_size, row_size

