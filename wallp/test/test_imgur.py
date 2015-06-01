from unittest import TestCase, main as ut_main
import sys

from wallp.util.logger import log
from wallp.service.imgur import Imgur


page = None, 0


class TestImgur(TestCase):
	def __init__(self, *args, **kwargs):
		self._imgur_pages = [	('http://imgur.com/gallery/moboUHY', 1),
					('http://imgur.com/gallery/QKz1d', 3),
					('http://imgur.com/a/SAjtQ', 6),
					('http://imgur.com/gallery/THfdT', 18),
					('http://imgur.com/gallery/K3bYZ', 67),
					('http://imgur.com/gallery/wCBYO', 2163),
					('http://imgur.com/gallery/hfHhb', 625),
					('http://imgur.com/gallery/D3vya', 976)]
					#('http://imgur.com/gallery/5vKwE', 20000)] fix: no truncated div, js load

		if page[0] is not None:
			self._imgur_pages = [page]

		super(TestImgur, self).__init__(*args, **kwargs)


	def setUp(self):
		log.clear_testresult()


	def test_get_image_url_from_page(self):
		imgur = Imgur()

		for page in self._imgur_pages:
			log.clear_testresult()
			log.debug('\ntest page: %s'%page[0])
			url = imgur.get_image_url_from_page(page[0])
			tr = log.get_testresult()

			self.assertEquals(page[1], tr[0], msg='failed for page: %s'%page[0])
			self.assertTrue(url.startswith('http'))


if __name__ == '__main__':
	if len(sys.argv) > 3:
		page = sys.argv[2], int(sys.argv[3])
		del sys.argv[2:]
	ut_main()
