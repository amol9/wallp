
from ..proto.server_pb2 import Response


class ImageResponse():
	def __init__(self, wp_image):
		self._wp_image = wp_image
		self._chunk_no = 0
		self._abort = False

	
	def get_next_chunk(self):
		response = Response()
		last_chunk = False

		if not self._abort:
			chunk = self._wp_image.chunk(self._chunk_no)

			if self._chunk_no + 1 == self._wp_image.chunk_count:
				last_chunk = True
			else:
				self._chunk_no += 1

			response.type = Response.IMAGE_CHUNK
			response.image_chunk.data = chunk
		else:
			response.type = Response.IMAGE_ABORT
			last_chunk = True

		return response.SerializeToString(), last_chunk


	def abort(self):
		self._abort = True

