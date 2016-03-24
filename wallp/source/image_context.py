
class ImageContext:
	def __init__(self, title=None, description=None, artist=None, url=None):
		self.title 		= title
		self.description 	= description
		self.artist 		= artist
		self.url		= url

	
	def __repr__(self):
		if self.description is None:
			desc_len = 0
			desc = None
		else:
			desc_len = len(self.description)
			desc = self.description[0: 1024]

		repr = 'title: %s\ndesc: %s\ndesc len: %d\nartist: %s\ncontext url: %s' \
			%(self.title, desc, desc_len, self.artist, self.url)
		return repr

