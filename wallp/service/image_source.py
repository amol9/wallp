
class ImageSource:
	def __init__(self):
		self.title = None
		self.description = None
		self.artist = None

	
	def __repr__(self):
		repr = 'title: %s\ndesc: %s\nartist: %s'%(self.title, self.description, self.artist)
		return repr

