
from .fixed_length_message import FixedLengthMessage
from ..proto.server_pb2 import Response
from ..proto.client_pb2 import Request
from .wp_change_message import WPState
from .image_chunk_producer import ImageChunkProducer


class WallpServer(FixedLengthMessage):
	def __init__(self, server_shared_data):
		FixedLengthMessage.__init__(self)
		self._server_shared_data = server_shared_data


	def messageReceived(self, message):
		request = Request()
		request.ParseFromString(message)

		response = Response()

		wp_image = self._server_shared_data.wp_image
		wp_state = self._server_shared_data.wp_state

		import binascii
		print 'processing request..', binascii.hexlify(message), '  ', len(message)
		print 'request type: ', request.type

		if request.type == Request.FREQUENCY:
			response.type = Response.FREQUENCY
			response.frequency.value = self.get_frequency()

		elif request.type == Request.LAST_CHANGE:
			response.type = Response.LAST_CHANGE
			response.last_change.timestamp = self.get_last_change() #self._server_shared_data.last_change

		elif request.type == Request.IMAGE:
			if wp_state == WPState.READY:
				response.type = Response.IMAGE_INFO
				image_info = response.image_info

				image_info.extension = wp_image.extension
				image_info.length = wp_image.length
				image_info.chunk_count = wp_image.chunk_count

				self.transport.registerProducer(ImageChunkProducer(self.transport, wp_image))

			elif wp_state == WPState.CHANGING:
				response.type = Response.IMAGE_CHANGING

			elif wp_state == WPState.NONE:
				response.type = Response.IMAGE_NONE

			else:
				#log / handle error
				return


		else:
			response.type = Response.BAD_REQUEST

		print 'response type: ', response.type

		self.sendMessage(response.SerializeToString())


	def get_frequency(self):
		return '1h'


	def get_last_change(self):
		return 0


