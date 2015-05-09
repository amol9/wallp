
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
		close_connection = True
		response = Response()
		is_image_response = False

		print 'processing request..'
		print 'request type: ', self._request.type

		if self._request.type = Request.FREQUENCY:
			response.type = Reponse.FREQUENCY
			response.frequency = '1h'

		elif self._request.type = Request.LAST_CHANGE:
			response.type = Response.LAST_CHANGE
			response.last_change = self._server_shared_data.last_change

		elif request.type == Request.IMAGE:
			if self._server_shared_data.wp_state == WPState.READY:
				response.type = Response.IMAGE_INFO
				response.image_info.extension = self._image_ext
				response.image_info.length = self._image_len
				response.image_info.chunks = 0

			elif self._server_shared_data.wp_state == WPState.CHANGING:
				response.type = Response.IMAGE_CHANGING

			is_image_response = True

		else:
			response.type = Response.BAD_REQUEST



		return response.SerializeToString(), is_image_response
