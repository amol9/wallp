
from mayloop.protocol.fixed_length_message import FixedLengthMessage
from .protobuf.server_pb2 import Response
from .protobuf.client_pb2 import Request
from .wp_change_message import WPState
from .image_chunk_producer import ImageChunkProducer
from ...util.logger import log


class WallpServer(FixedLengthMessage):
	def __init__(self, wp_state, wp_image):
		FixedLengthMessage.__init__(self)
		self._wp_state = wp_state
		self._wp_image = wp_image


	def messageReceived(self, message):
		request = Request()
		request.ParseFromString(message)

		response = Response()

		log.debug('request type: %d'%request.type)

		if request.type == Request.FREQUENCY:
			response.type = Response.FREQUENCY
			response.frequency.value = self.get_frequency()

		elif request.type == Request.LAST_CHANGE:
			response.type = Response.LAST_CHANGE
			response.last_change.timestamp = self.get_last_change() #self._server_shared_data.last_change

		elif request.type == Request.IMAGE:
			if self.wp_state == WPState.READY:
				response.type = Response.IMAGE_INFO
				image_info = response.image_info

				image_info.extension = self._wp_image.extension
				image_info.length = self._wp_image.length
				image_info.chunk_count = self._wp_image.chunk_count

				self.transport.registerProducer(ImageChunkProducer(self.transport, self._wp_image))
				self.transport.closeAfterWriteComplete()

			elif self.wp_state == WPState.CHANGING:
				response.type = Response.IMAGE_CHANGING

			elif self.wp_state == WPState.NONE:
				response.type = Response.IMAGE_NONE

			else:
				log.error('something bad happened, wp state is set to %d'%self.wp_state)
				response.type = Response.SERVER_ERROR


		else:
			response.type = Response.BAD_REQUEST

		log.debug('response type: %d'%response.type)

		self.sendMessage(response.SerializeToString())


	def get_frequency(self):
		return '1h'


	def get_last_change(self):
		return 0


	def get_wp_state(self):
		return self._wp_state.state


	def set_wp_state(self, state):
		self._wp_state.state = state


	wp_state = property(get_wp_state, set_wp_state)

