from unittest import TestCase, main as ut_main
import random

from wallp.db import ItemList, ImgurAlbumList, DBSession, Base, ImgurAlbum, NotFoundError
from wallp.test.utils import order, replace_default_testcase_sort_order


replace_default_testcase_sort_order()


class TestItemList(TestCase):
	db_path 	= 'test.db'
	album_list 	= []
	bad_item_list	= ['', None, '1', 'a', 'htt://imgur.com/rwef', 'http://google.com/123']
	item_count	= 100
	album_url_base	= 'http://imgur.com/'
	disable_count	= 5
	random_trials	= 10

	@classmethod
	def setUpClass(cls):
		dbsession = DBSession(cls.db_path)
		ImgurAlbum.__table__.create(bind=dbsession.bind)

		charlist = [chr(i) for i in range(48, 58) + range(97, 123)]	#0-9 a-z
		for i in range(cls.item_count):					#create a list of random imgur urls
			cls.album_list.append(cls.album_url_base + ''.join(random.sample(charlist, 8)))


	@order(1)
	def test_add(self):
		imgur_album_list = ImgurAlbumList()
		dbsession = DBSession()

		for item in self.album_list:
			imgur_album_list.add(item, True)
		dbsession.commit()

		rowcount = dbsession.query(ImgurAlbum).count()
		self.assertEquals(rowcount, self.item_count)

		for item in self.bad_item_list:
			with self.assertRaises(ValueError) as e:
				imgur_album_list.add(item, True)

		rowcount = dbsession.query(ImgurAlbum).count()
		self.assertEquals(rowcount, self.item_count)


	@order(2)
	def test_disable(self):
		imgur_album_list = ImgurAlbumList()
		dbsession = DBSession()

		for i in range(self.disable_count):
			imgur_album_list.disable(self.album_list[i])

		rowcount = dbsession.query(ImgurAlbum).filter(ImgurAlbum.enabled == False).count()
		self.assertEquals(rowcount, self.disable_count)

		for item in self.bad_item_list:
			with self.assertRaises(NotFoundError) as e:
				imgur_album_list.enable(item)


	@order(3)
	def test_enable(self):
		imgur_album_list = ImgurAlbumList()
		dbsession = DBSession()

		for i in range(self.disable_count):
			imgur_album_list.enable(self.album_list[i])

		rowcount = dbsession.query(ImgurAlbum).filter(ImgurAlbum.enabled == True).count()
		self.assertEquals(rowcount, self.item_count)


	@order(4)
	def test_get_random(self):
		imgur_album_list = ImgurAlbumList()

		random_urls = []

		for i in range(self.random_trials):
			url = imgur_album_list.get_random()
			self.assertNotEquals(url, None)
			self.assertNotEquals(url, '')
			random_urls.append(url)

		uniq_urls_count = len(list(set(random_urls)))
		self.assertGreater(uniq_urls_count, len(random_urls) / 2)


if __name__ == '__main__':
	ut_main()

