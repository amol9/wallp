
from . import ImgurAlbum, Subreddit, SearchTerm


class ItemList:
	item_type = None
	column = None
	
	def get_random(self):
		pass


	def enable(self, value):
		pass


	def disable(self, value):
		pass


	def add(self, value):
		pass



class ImgurAlbumList(ItemList):
	item_type = ImgurAlbum
	column = 'url'


class SubredditList(ItemList):
	item_type = Subreddit
	column = 'name'


class SearchTermList(ItemList):
	item_type = SearchTerm
	column = 'term'




