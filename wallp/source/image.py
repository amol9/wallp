

class Image:

	def __init__(self, url=None, title=None, description=None, user=None, context_url=None, width=None, height=None, ext=None, 
			size=None, date=None, rank=None, score=None):

		self.url		= url
		self.title		= title
		self.description	= description
		self.user		= user
		self.context_url	= context_url
		self.width		= width
		self.height		= height
		self.ext		= ext
		self.size		= size
		self.date		= date
		self.rank		= rank
		self.score		= score

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


	def init_from_db_image(self, db_image):
		self.url		= db_image.url
		self.title		= db_image.title
		self.description	= db_image.description
		self.user		= db_image.artist
		self.context_url	= db_image.context_url
		self.width		= db_image.width
		self.height		= db_image.height
		
		self.db_image		= db_image

