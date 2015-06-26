
class ImageSource:
	def __init__(self, title=None, description=None, artist=None, context_url=None):
		self.title 		= None
		self.description 	= None
		self.artist 		= None
		self.context_url	= None

	
	def __repr__(self):
		repr = 'title: %s\ndesc: %s\nartist: %s\ncontext url: %s'%(self.title, self.description, self.artist, self.context_url)
		return repr

