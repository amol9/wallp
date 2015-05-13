from unittest import TestCase, main as ut_main

from wallp.wallp_server import WallpServer
from wallp.service import ServiceException


class TestWallpServer(TestCase):

	def test_get_image(self):
		wp_server = WallpServer()
	
		try:
			wp_server.get_image()
		except ServiceException:
			print 'service exception'
			self.fail()


if __name__ == '__main__':
	ut_main()

