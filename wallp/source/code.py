import tempfile
import os
from time import time
from io import BytesIO
from os.path import abspath, join as joinpath
import random

from redlib.api.colors import colorlist
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import ImageFormatter
from pygments.util import ClassNotFound
from pygments import highlight
from PIL import Image as PILImage

from ..util.logger import log
from .base import SourceError, SourceParams, Source
from .image import Image
from .trace import Trace
from ..desktop.desktop_factory import get_desktop


def src_path():
	path = os.sep.join(abspath(__file__).split(os.sep)[0: -2])
	src_files = []

	for root, _, files in os.walk(path):
		for fname in files:
			fname.endswith('.py') and src_files.append(joinpath(root, fname))

	return random.choice(src_files)


class CodeParams(SourceParams):
	name = 'code'

	def __init__(self, filepath=src_path(), font_name=None, font_size=14):
		self.filepath 	= filepath
		self.font_name	= font_name
		self.font_size	= font_size


class Code(Source):
	name 		= 'code'
	params_cls 	= CodeParams
	online		= False
	db		= False
	gen		= True

	
	def __init__(self):
		self._trace = Trace()


	def get_image(self, params):
		return self.generate_image(params)		


	def generate_image(self, params):
		filepath = params.filepath

		try:
			lexer = get_lexer_for_filename(filepath)
		except ClassNotFound as e:
			log.error(e)
			raise SourceError(str(e))

		if lexer is None:
			raise SourceError('cannot find a lexer for %s'%filepath)

		self._trace.add_step('source file', filepath)
		self._trace.add_step('detected language', lexer.name.lower())

		formatter = ImageFormatter(font_name=params.font_name, font_size=params.font_size, line_numbers=False)

		code = None
		with open(filepath, 'r') as f:
			code = f.read()

		output = BytesIO(highlight(code, lexer, formatter))

		im = PILImage.open(output)

		dt = get_desktop()
		dw, dh = dt.get_size()

		if im.height > dh:
			im = im.crop((0, 0, im.width, dh))

		image = Image()
		image.i_width, image.i_height = im.width, im.height

		fn, temp_filepath = tempfile.mkstemp()
		f = os.fdopen(fn, 'wb')

		im.save(f, 'png')
		f.close()
		im.close()

		image.ext = image.type = 'png'
		image.temp_filepath = temp_filepath

		return image


	def get_trace(self):
		return self._trace.steps

