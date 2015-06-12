
class WPStyle:
	NONE  		= 0
	TILED 		= 1
	CENTERED 	= 2 
	SCALED 		= 3 
	STRETCHED 	= 4 
	ZOOM 		= 5 

	strings = [
	'none',
	'tiled',
	'centered',
	'scaled',
	'stretched',
	'zoom'
	]

	@classmethod
	def to_string(cls, style):
		if 0 <= style < len(cls.strings):
			return cls.strings[style]
		else:
			return 'invalid style'
