
from ..util.logger import log


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


def compute_style(im_width, im_height, dt_width, dt_height):
	assert type(im_width) == int
	assert type(im_height) == int

	log.debug('image: width=%d, height=%d'%(im_width, im_height))
	log.debug('desktop: width=%d, height=%d'%(dt_width, dt_height))

	style = None

	if im_width < 5 and im_height < 5:
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

	log.debug('style: %s'%style)

	return style

