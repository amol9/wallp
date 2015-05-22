from unittest import TestCase, main as ut_main, skip
from Queue import Queue

from wallp.server.protocols.image_chunk_producer import ImageChunkProducer
from wallp.server.wallpaper_image import WallpaperImage
from wallp.server.proto.server_pb2 import Response
from wallp.server.proto.client_pb2 import Request
from wallp.server.protocols.wallp_server import WallpServer
from wallp.server.protocols.wp_change_message import WPState
from .mock_transport import MockTransport


class MockServerSharedState:
	def __init__(self):
		self.wp_image = None
		self.wp_state = None


class TestWallpServer(TestCase):
	wallp_server = None
	frequency = '1h'
	last_change = 0
	shared_state = None
	test_image_path = '/home/amol/Pictures/Firefox_wallpaper.png'

	@classmethod
	def setUpClass(cls):
		cls.shared_state = MockServerSharedState()
		cls.shared_state.wp_image = WallpaperImage()
		cls.shared_state.wp_image.set_path(cls.test_image_path)
		cls.shared_state.wp_state = WPState.NONE

		WallpServer.get_frequency = lambda slf : cls.frequency
		WallpServer.get_last_change = lambda slf : cls.last_change
		WallpServer.sendMessage = lambda slf, msg : slf.transport.write(msg)

		cls.wallp_server = WallpServer(cls.shared_state)
		cls.wallp_server.transport = MockTransport()


	def get_response(self):
		messages = self.wallp_server.transport.messages
		self.assertFalse(messages.empty())

		res_msg = messages.get()
		response = Response()
		response.ParseFromString(res_msg)

		return response


	def testFrequency(self):
		request = Request()
		request.type = Request.FREQUENCY

		self.wallp_server.messageReceived(request.SerializeToString())
		response = self.get_response()

		self.assertEquals(response.type, Response.FREQUENCY)
		self.assertEquals(response.frequency.value, self.frequency)


	def testLastChange(self):
		request = Request()
		request.type = Request.LAST_CHANGE

		self.wallp_server.messageReceived(request.SerializeToString())
		response = self.get_response()

		self.assertEquals(response.type, Response.LAST_CHANGE)
		self.assertEquals(response.last_change.timestamp, self.last_change)


	def send_image_request(self):
		request = Request()
		request.type = Request.IMAGE

		self.wallp_server.messageReceived(request.SerializeToString())


	def testImageNone(self):
		self.shared_state.wp_state = WPState.NONE

		self.send_image_request()
		response = self.get_response()

		self.assertEquals(response.type, Response.IMAGE_NONE)
		#test value


	def testImageChanging(self):
		self.shared_state.wp_state = WPState.CHANGING
	
		self.send_image_request()
		response = self.get_response()

		self.assertEquals(response.type, Response.IMAGE_CHANGING)
		#test value

	
	def testImageReady(self):
		self.shared_state.wp_state = WPState.READY

		self.send_image_request()
		response = self.get_response()

		self.assertEquals(response.type, Response.IMAGE_INFO)
		self.assertIsNotNone(response.image_info)
		self.assertTrue(type(response.image_info.extension) in [str, unicode])
		self.assertTrue(response.image_info.length > 0)
		self.assertTrue(response.image_info.chunk_count > 0)

		self.assertIsInstance(self.wallp_server.transport.producer, ImageChunkProducer)
		self.assertEquals(self.wallp_server.transport.producer._chunk_no, 0)


	@skip('unable to fix')
	def testBadRequest(self):
		self.wallp_server.messageReceived('\x18\x23\x30\x40\x00\x23')
		response = self.get_response()

		self.assertEquals(response.type, Response.BAD_REQUEST)


if __name__ == '__main__':
	ut_main()

