

class Image:

	def __init__(self, url=None, title=None, description=None, user=None, context_url=None, width=None, height=None, ext=None, size=None):
		self.url		= url
		self.title		= title
		self.description	= description
		self.user		= user
		self.context_url	= context_url
		self.width		= width
		self.height		= height
		self.ext		= ext
		self.size		= size

		# to be filled in by get_image_info() by scanning the actual image data
		self.type		= None
		self.i_width		= None
		self.i_height		= None

		# temp filepath after image is downloaded
		self.temp_filepath	= None

		# filepath if an existing local image is being used
		self.filepath		= None

		# if an already used image is being reused from the db
		self.db_image		= None

