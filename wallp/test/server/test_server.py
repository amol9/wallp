from unittest import TestCase, main as ut_main

from wallp.server.server import Server
from wallp.manager import Manager


port = 40001

class TestServer(TestCase):
	def test_server_start(self):
		server = Server(port)
		server.start()


	def test_client(self):
		Manager.parse_args = lambda x : None
		Manager.set_frequency = lambda x : None

		cl = Manager()
		cl.get_image_from_wallp_server('localhost,' + str(port))


if __name__ == '__main__':
	ut_main()

