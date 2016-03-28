
from ..util.logger import log
from ..db.app.config import Config
from ..util.printer import printer


class WPStyleError(Exception):
	pass


class WPStyle:
	NONE  		= 0
	TILED 		= 1
	CENTERED 	= 2 
	SCALED 		= 3 
	STRETCHED 	= 4 
	ZOOM 		= 5 

	strings = ['none', 'tiled', 'centered', 'scaled', 'stretched', 'zoom']

	def __init__(self, style):
		if type(style) == int:
			if style < self.NONE or style > self.ZOOM:
				raise WPStyleError('invalid style: %d'%style)

			self._style = style
		elif type(style) == str:
			if not style in self.strings:
				raise WPStyleError('invalid style: %s'%style)

			self._style = self.strings.index(style)
		else:
			raise WPStyleError('invalid style type: %s'%type(style))


	def __str__(self):
		return self.strings[self._style]


	def __int__(self):
		return self._style


	#def __eq__(self, other):
	#	return self._style == other._style


def compute_style(im_width, im_height, dt_width, dt_height):
	log.debug('image: width=%d, height=%d'%(im_width, im_height))
	printer.printf('image dimensions', '%dx%d'%(im_width, im_height), verbosity=3)
	log.debug('desktop: width=%d, height=%d'%(dt_width, dt_height))
	printer.printf('desktop dimensions', '%dx%d'%(dt_width, dt_height), verbosity=3)

	style = None
	tiled_size = Config().get('style.tiled_size')

	if im_width == dt_width and im_height == dt_height:
		style = WPStyle(WPStyle.CENTERED)

	elif im_width <= tiled_size and im_height <= tiled_size:
		style = WPStyle(WPStyle.TILED)

	else:
		dt_ar = float(dt_width) / dt_height
		im_ar = float(im_width) / im_height
		
		wr = float(im_width) / dt_width
		hr = float(im_height) / dt_height

		if (wr >= 0.9) or (hr >= 0.9):
			style = WPStyle(WPStyle.SCALED)
		else:
			style = WPStyle(WPStyle.CENTERED)

	log.debug('calculated style: %s'%style)
	printer.printf('wallpaper style', str(style), verbosity=3)

	return style

