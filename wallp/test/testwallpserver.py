from unittest import TestCase, main as ut_main

from wallp.server.wallpserver import WallpServer


class TestWallpServer(TestCase):
	def test_server(self):
		port = 40001
		server = WallpServer(port)
		server.start_select()


if __name__ == '__main__':
	ut_main()

