from unittest import TestCase, main as ut_main


from wallp.db import ItemList, ImgurAlbumList


class TestItemList(TestCase):
	db_path 	= 'test.db'
	album_list 	= []
	bad_item_list	= ['', None, '1', 'a', 'htt://imgur.com/rwef', 'http://google.com/123']
	item_count	= 100
	album_url_base	= 'http://imgur.com/'
	disable_count	= 5

	@classmethod
	def setUpClass(cls):
		dbsession = DBSession(cls.db_path)

		Base.metadata_create(ImgurAlbumList) #???

		charlist = [chr(i) for i in range(48, 58) + range(97, 123)]	#0-9 a-z
		for i in range(cls.item_count):
			cls.album_list.append(cls.album_url_base + random.sample(charlist, 8))


	def test_add(self):
		imgur_album_list = ImgurAlbumList()
		dbsession = DBSession()

		for item in self.album_list:
			imgur_album_list.add(item, True)
		dbsession.commit()

		rowcount = dbsession.query(ImgurAlbumList).count()
		self.assertEquals(rowcount, self.item_count)

		for item in self.bad_item_list:
			with self.assertRaises(ValueError) as e:
				imgur_album_list.add(item, True)

		rowcount = dbsession.query(ImgurAlbumList).count()
		self.assertEquals(rowcount, self.item_count)


	def test_disable(self):
		imgur_album_list = ImgurAlbumList()

		for i in range(self.disable_count):
			imgur_album_list.disable(self.album_list[i])

		rowcount = dbsession.query(ImgurAlbumList).filter(ImgurAlbumList.enabled == False).count()
		self.assertEquals(rowcount, self.disable_count)

		for item in self.bad_item_list:
			with self.assertRaises(NotFoundError) as e:
				imgur_album_list.enable(item)


	def test_enable(self):
		imgur_album_list = ImgurAlbumList()

		for i in range(self.disable_count):
			imgur_album_list.enable(self.album_list[i])

		rowcount = dbsession.query(ImgurAlbumList).filter(ImgurAlbumList.enabled == True).count()
		self.assertEquals(rowcount, self.item_count)


	def test_get_random(self):
		imgur_album_list = ImgurAlbumList()


