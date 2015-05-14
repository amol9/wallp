from unittest import TestCase, main as ut_main
from threading import Thread
from time import sleep

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


	def test_load(self):
		exceptions = [0]
		def thread_func(exceptions):
			wp_server = WallpServer()
			try:
				wp_server.get_image()
			except Exception as e:
				#print 'exception in thread', type(e)
				import traceback; traceback.print_exc()
				#raw_input()
				exceptions[0] += 1

		n = 500
		threads = []
		for i in range(0, n):
			t = Thread(target=thread_func, args=(exceptions,))
			t.start()
			threads.append(t)

		for i in range(0, n):
			threads[i].join()

		print 'all %d threads finished, failed: %d'%(n, exceptions[0])


if __name__ == '__main__':
	ut_main()

