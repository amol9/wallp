from unittest import TestCase, main as ut_main
from random import randint
from Queue import Queue
import os

from wallp.server.protocols.image_chunk_producer import ImageChunkProducer
from wallp.server.wallpaper_image import WallpaperImage
from wallp.server.proto.server_pb2 import Response


class MockTransport:
	def __init__(self):
		self.messages = Queue()
		self.unregistered = False
	

	def write(self, message):
		self.messages.put(message)


	def unregisterProducer(self):
		self.unregistered = True


class TestImageChunkProducer(TestCase):
	wp_image = None
	test_image_path = '/home/amol/Pictures/Firefox_wallpaper.png'

	@classmethod
	def setUpClass(cls):
		cls.wp_image = WallpaperImage()
		cls.wp_image.set_path(cls.test_image_path)


	@classmethod
	def tearDownClass(cls):
		pass


	def tearDown(self):
		pass

	
	def testFullImage(self):
		transport = MockTransport()
		icp = ImageChunkProducer(transport, self.wp_image)

		while not transport.unregistered:
			icp.resumeProducing()


		image = ''
		while not transport.messages.empty():
			response = Response()
			response.ParseFromString(transport.messages.get()[4:])		#ignoring length prefix

			self.assertEquals(response.type, Response.IMAGE_CHUNK)
			image += response.image_chunk.data

		image_size = os.stat(self.test_image_path).st_size
		self.assertEquals(len(image), image_size)



	def testAbort(self):
		transport = MockTransport()
		icp = ImageChunkProducer(transport, self.wp_image)

		abort_after_chunk_no = randint(0, self.wp_image.chunk_count - 2)
		chunk_no = 0
		while not transport.unregistered:
			icp.resumeProducing()
			if chunk_no == abort_after_chunk_no:
				icp.stopProducing()
			chunk_no += 1


		chunk_no = 0
		while not transport.messages.empty():
			response = Response()
			response.ParseFromString(transport.messages.get()[4:])		#ignoring length prefix
			
			if chunk_no <= abort_after_chunk_no:
				self.assertEquals(response.type, Response.IMAGE_CHUNK)
			else:
				self.assertEquals(response.type, Response.IMAGE_ABORT)
				continue
			chunk_no += 1


		self.assertTrue(transport.messages.empty())


if __name__ == '__main__':
	ut_main()

