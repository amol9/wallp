from unittest import TestCase, main as ut_main, skip
import sys

from wallp.util.logger import log
from wallp.service.imgur import Imgur
from wallp.service import ServiceError 


class TestImgur(TestCase):
	args = []
	imgur_pages = [	('http://imgur.com/gallery/moboUHY', 1),
			('http://imgur.com/gallery/BZFHk5l', 1),
			('http://imgur.com/gallery/QKz1d', 3),
			('http://imgur.com/a/SAjtQ', 6),
			('http://imgur.com/gallery/THfdT', 18),
			('http://imgur.com/gallery/K3bYZ', 67),
			('http://imgur.com/gallery/wCBYO', 2163),
			('http://imgur.com/gallery/hfHhb', 625),
			('http://imgur.com/gallery/D3vya', 976),
			('http://imgur.com/oGevSWm', 1)]
			#('http://imgur.com/gallery/5vKwE', 20000)] fix: no truncated div, js load


	@classmethod
	def setUpClass(cls):
		pass


	@skip('old')
	def test_get_image_url_from_page(self):
		imgur = Imgur()

		for page in self._imgur_pages:
			log.debug('\ntest page: %s'%page[0])
			url = imgur.get_image_url_from_page(page[0])
			tr = log.get_testresult()

			self.assertEquals(page[1], tr[0], msg='failed for page: %s'%page[0])
			self.assertTrue(url.startswith('http'))

	@skip('temp')
	def test_pages_with_single_image(self):
		imgur = Imgur()
		
		for page in self.imgur_pages:
			if page[1] == 1:
				url, icount = imgur.get_image_url_from_page(page[0])
				self.assertIsNotNone(url)
				self.assertTrue(url.startswith('http'))
				self.assertEqual(icount, 1)


	def test_all_pages(self):
		imgur = Imgur()

		for page in self.imgur_pages:
			url, icount = imgur.get_image_url_from_page(page[0])
			self.assertIsNotNone(url)
			self.assertTrue(url.startswith('http'), msg=url)
			self.assertEqual(icount, page[1])
			self.validate_image_url(url)
			print imgur._image_source


	def try_command_args(self):
		imgur = Imgur()

		for url in self.args:
			try:
				iurl, icount = imgur.get_image_url_from_page(url)
				print('image count:', icount)
			except ServiceError as e:
				print(str(e))


	def validate_image_url(self, url):
		self.assertIsNotNone(url)
		self.assertTrue(url.startswith('http'))
		self.assertIn(url[url.rfind('.') + 1 : ], ['jpg', 'jpeg', 'bmp', 'png'])


if __name__ == '__main__':
	log.start('stdout', log.levels['debug'])

	for arg in sys.argv[1:]:
		if arg.startswith('http'):
			TestImgur.args.append(arg)
			sys.argv.remove(arg)
			sys.argv.append('TestImgur.try_command_args')
	
	ut_main()
