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
		count = self._dbsession.query(func.count(self.itemtype))
		item_offset = randint(1, count)

		seen = 0
		while seen < count:
			result = self.itemtype.query().limit(1).offset(item_offset)
			item = result[0]
			if not item.enabled:
				seen += 1
				item_offset += 1
				if item_offset > count:		#wrap around
					item_offset = 1
				continue

			return getattr(item, self.column)

		raise NotFoundError('no %s found'%self.column)


	def enable(self, value):
		self.set_enabled(value, True)


	def disable(self, value):
		self.set_enabled(value, False)


	def set_enabled(self, value, state):
		item = self.get_item(value)
		item.enabled = state

		self._dbsession.commit()


	def get_item(self, value):
		column_type = getattr(self.itemtype, self.column)
		result = self.itemtype.query().filter(column_type == value).all()

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




