from zope.interface import Interface, Attribute, implementer
import re
import random

from . import ImgurAlbum, Subreddit, SearchTerm, DBSession
from .regex import Regex
from .exc import NotFoundError


class IItemList(Interface):
	itemtype 	= Attribute('item type')
	column 		= Attribute('column name')
	regex		= Attribute('regex to validate item value')
	
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
		self.validate(value)

		cols = {self.column : value, 'enabled': enabled}
		item = self.itemtype(**cols)

		self._dbsession.add(item)
		if commit:
			self._dbsession.commit()


	def validate(self, value):
		if value is None:
			raise ValueError('value none')

		column_type = getattr(self.itemtype, self.column)
		max_len = column_type.property.columns[0].type.length

		if len(value) > max_len:
			raise ValueError('value longer than %d characters'%max_len)

		c_regex = re.compile(self.regex.expression)

		if not c_regex.match(value):
			raise ValueError(self.regex.err_msg)
	

	def get_random(self):
		count = self._dbsession.query(self.itemtype).count()
		item_offset = random.randint(0, count - 1)

		seen = 0
		while seen < count:
			result = self._dbsession.query(self.itemtype).limit(1).offset(item_offset).all()
			item = result[0]
			if not item.enabled:
				seen += 1
				item_offset += 1
				if item_offset > (count - 1):		#wrap around
					item_offset = 0
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
		result = self._dbsession.query(self.itemtype).filter(column_type == value).all()

		if (len(result) == 0):
			raise NotFoundError('%s not found'%value)

		if (len(result) > 0):
			#do something to correct
			pass

		return result[0]


class ImgurAlbumList(ItemList):
	name		= 'imgur-album'
	itemtype 	= ImgurAlbum
	column 		= 'url'
	regex 		= Regex("https?://imgur.com/\w+", 'imgur url be like http://imgur.com/...')

	def set_image_count(self, url, count):
		imgur_album = self.get_item(url)
		imgur_album.image_count = count

		self._dbsession.commit()


class SubredditList(ItemList):
	name		= 'subreddit'
	itemtype 	= Subreddit
	column 		= 'name'
	regex		= Regex("[a-zA-Z]\w+", 'not a good subreddit name, is it? gotta start with an alphabet.')


class SearchTermList(ItemList):
	name		= 'search-term'
	itemtype 	= SearchTerm
	column 		= 'term'
	regex		= Regex(".*", 'are you kidding me?')

