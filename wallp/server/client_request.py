

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
		response = None
		is_image_response = False

		print 'processing request..'
		print 'request type: ', self._request.type

		if self._request.type = Request.FREQUENCY:
			response = '1h'

		elif self._request.type = Request.LAST_CHANGE:
			response = self._last_change

		elif request.type == Request.IMAGE:
			if self._state == 'ready':
				response = Response()
				response.type = Response.IMAGE_INFO
				response.image_info.extension = self._image_ext
				response.image_info.length = self._image_len
				response.image_info.chunks = 0

			elif self._state == 'in_progress':
				response = 'in-progress'

			is_image_response = True

		else:
			response = 'bad-command'



		return response.SerializeToString(), is_image_response
