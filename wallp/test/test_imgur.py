from unittest import TestCase, main as ut_main, skip
import sys
from os.path import exists
import os

from wallp.util.logger import log
from wallp.service.imgur import Imgur
from wallp.service import ServiceError 

from .db.util import create_db


class TestImgur(TestCase):
	args = []
	db_path = 'test_imgur.db'
	imgur_pages = [	('http://imgur.com/gallery/moboUHY', 	1),
			('http://imgur.com/gallery/BZFHk5l', 	1),
			('http://imgur.com/gallery/QKz1d', 	3),
			('http://imgur.com/a/SAjtQ', 		6),
			('http://imgur.com/gallery/THfdT', 	18),
			('http://imgur.com/gallery/K3bYZ', 	67),
			('http://imgur.com/gallery/wCBYO', 	2163),
			('http://imgur.com/gallery/hfHhb', 	625),
			('http://imgur.com/gallery/D3vya', 	976),
			('http://imgur.com/oGevSWm', 		1),
			('http://imgur.com/gallery/0nCDJ', 	18)]
			#('http://imgur.com/gallery/5vKwE', 	20000)] fix: no truncated div, js load


	@classmethod
	def setUpClass(cls):
		create_db(cls.db_path)


	@classmethod
	def tearDownClass(cls):
		if exists(cls.db_path):
			os.remove(cls.db_path)


	@skip('temp')
	def test_pages_with_single_image(self):
		for page in self.imgur_pages:
			if page[1] == 1:
				imgur = Imgur()
				url = imgur.get_image_url_from_page(page[0])
				self.assertIsNotNone(url)
				self.assertTrue(url.startswith('http'))
				self.assertEqual(imgur._image_count, 1)


	def validate_image_url(self, url):
		self.assertIsNotNone(url)
		self.assertTrue(url.startswith('http'))
		#self.assertIn(url[url.rfind('.') + 1 : ], ['jpg', 'jpeg', 'bmp', 'png'])


	def test_all_pages(self):
		for page in self.imgur_pages:
			imgur = Imgur()
			url = imgur.get_image_url_from_page(page[0])
			self.validate_image_url(url)

			icount = imgur.get_image_count()
			icount = 1 if icount == 1 else icount + 1
			self.assertEqual(icount, page[1])


	def test_search(self):
		imgur = Imgur()

		for i in range(5):
			url = imgur.get_image_url_from_search(None)
			self.validate_image_url(url)


	def try_command_args(self):
		imgur = Imgur()

		for url in self.args:
			try:
				iurl = imgur.get_image_url_from_page(url)
			except ServiceError as e:
				print(str(e))


if __name__ == '__main__':
	log.start('stdout', log.levels['debug'])

	for arg in sys.argv[1:]:
		if arg.startswith('http'):
			TestImgur.args.append(arg)
			sys.argv.remove(arg)
			sys.argv.append('TestImgur.try_command_args')
	
	ut_main()

