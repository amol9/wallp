from unittest import TestCase, main as ut_main

from wallp.server.wallpserver import WallpServer
from wallp.manager import Manager


class TestWallpServer(TestCase):
	def test_server(self):
		port = 40001
		server = WallpServer(port)
		server.start()


	def test_client(self):
		Manager.parse_args = lambda x : None
		Manager.set_frequency = lambda x : None

		cl = Manager()
		cl.get_image_from_wallp_server('localhost,40001')


if __name__ == '__main__':
	ut_main()

