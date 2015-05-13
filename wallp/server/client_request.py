
from .server import WPState
from ..proto.client_pb2 import Request
from ..proto.server_pb2 import Response


class ClientRequest():
	def __init__(self, request_string, server_shared_data):
		try:
			self._request = Request()
			self._request.ParseFromString(request_string)

		except DecoderError as e:
			#log
			raise Exception()

		self._server_shared_data = server_shared_data


	def process(self):
		keep_alive = True
		response = Response()
		is_image_response = False

		wp_image = self._server_shared_data.wp_image
		wp_state = self._server_shared_data.wp_state

		print 'processing request..'
		print 'request type: ', self._request.type

		if self._request.type == Request.FREQUENCY:
			response.type = Response.FREQUENCY
			response.frequency.value = '1h'

		elif self._request.type == Request.LAST_CHANGE:
			response.type = Response.LAST_CHANGE
			response.last_change.timestamp = 0 #self._server_shared_data.last_change

		elif self._request.type == Request.IMAGE:
			if wp_state == WPState.READY:
				response.type = Response.IMAGE_INFO
				image_info = response.image_info

				image_info.extension = wp_image.extension
				image_info.length = wp_image.length
				image_info.chunk_count = wp_image.chunk_count

				is_image_response = True

			elif wp_state == WPState.CHANGING:
				response.type = Response.IMAGE_CHANGING

			elif wp_state == WPState.NONE:
				response.type = Response.IMAGE_NONE
				keep_alive = False

			else:
				return None, False


		else:
			response.type = Response.BAD_REQUEST
			keep_alive = False


		return response.SerializeToString(), is_image_response, keep_alive
