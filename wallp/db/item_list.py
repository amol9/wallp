from zope.interface import Interface, Attribute

from . import ImgurAlbum, Subreddit, SearchTerm


class IItemList(Interface):
	itemtype 	= Attribute()
	column 		= Attribute()
	
	def get_random():
		'Get a random item from the list.'


	def enable(value):
		'Enable an item.'


	def disable(value):
		'Disable an item.'


	def add(value):
		'Add an item to the list.'


@implementer(IItemList)
class ItemList:
	def __init__(self):
		self._dbsession = DBSession()


	def add(self, value, enabled, commit=False):
		cols = {self.column : value, 'enabled': enabled}
		item = self.itemtype(**cols)

		self._dbsession.add(item)
		if commit:
			self._dbsession.commit()
	

	def get_random(self):
		count = self.itemtype.query().count()
		rand_id = randint(0, count)

		result = self.itemtype.query().filter(self.itemtype.id == rand_id).all()
		if (len(result) == 1):
			return result[0][self.column]

		result = self.itemtype.query().all()
		count = len(result)

		return choice(result)[column]


	def enable(self, value):
		self.set_enabled(value, True)


	def disable(self, value):
		self.set_enabled(value, False)


	def set_enabled(self, value, state):
		item = self.get_item(value)
		item.enabled = state

		self._dbsession.commit()


	def get_item(self, value):
		result = self.itemtype.query().filter(self.itemtype[column] == value).all()

		if (len(result) == 0):
			raise NotFoundError('%s not found'%value)

		if (len(result) > 0):
			#do something to correct
			pass

		return result[0]
	



class ImgurAlbumList(ItemList):
	itemtype = ImgurAlbum
	column = 'url'


class SubredditList(ItemList):
	itemtype = Subreddit
	column = 'name'


class SearchTermList(ItemList):
	itemtype = SearchTerm
	column = 'term'




