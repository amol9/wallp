from unittest import TestCase, main as ut_main
from threading import Thread
from time import sleep
import traceback
from Queue import Queue

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
		exc_queue = Queue()

		def thread_func(exceptions, exc_queue):
			wp_server = WallpServer()
			try:
				wp_server.get_image()
			except Exception as e:
				exceptions[0] += 1

				'''exc_file.lock('w|')
				traceback.print_exc(file=exc_file)
				exc_file.write('\n\n')
				exc_file.lock('u')'''
				exc_queue.put(traceback.format_exc())

		n = 500
		threads = []
		for i in range(0, n):
			t = Thread(target=thread_func, args=(exceptions, exc_queue))
			t.start()
			threads.append(t)

		for i in range(0, n):
			threads[i].join()

		with open('load_test_exc.log', 'w') as f:
			while not exc_queue.empty():
				f.write(exc_queue.get() + '\n\n')

		print 'all %d threads finished, failed: %d'%(n, exceptions[0])


if __name__ == '__main__':
	ut_main()

