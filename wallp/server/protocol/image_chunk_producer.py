from zope.interface import implements
import struct

from mayloop.imported.twisted.internet_interfaces import IPullProducer
from .protobuf.server_pb2 import Response
from ..wallpaper_image import WPImageError


class ImageChunkProducer:
	implements(IPullProducer)

	def __init__(self, transport, wp_image):
		self._transport = transport
		self._wp_image = wp_image
		self._chunk_no = 0
		self.producing = True


	def stopProducing(self):
		if self._chunk_no < self._wp_image.chunk_count:
			response = Response()
			response.type = Response.IMAGE_ABORT

			message = response.SerializeToString()
			message = struct.pack('>i', len(message)) + message

			self._transport.write(message)

		self.producing = False


	def resumeProducing(self):
		if self._chunk_no < self._wp_image.chunk_count:
			response = Response()
			response.type = Response.IMAGE_CHUNK
			try:
				response.image_chunk.data = self._wp_image.chunk(self._chunk_no)
			except WPImageError as e:
				log.error('cannot produce image chunk, aborting..')
				self.stopProducing()

			message = response.SerializeToString()
			message = struct.pack('>i', len(message)) + message

			self._transport.write(message)

			self._chunk_no += 1
		else:
			self.stopProducing()
		

