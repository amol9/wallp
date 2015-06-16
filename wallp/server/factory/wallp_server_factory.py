
from mayloop.imported.twisted.internet_protocol import Factory
from ..protocol.wallp_server import WallpServer


class WallpServerFactory(Factory):
	protocol = WallpServer

	def __init__(self, wp_state, wp_image):
		self._wp_state = wp_state
		self._wp_image = wp_image


	def buildProtocol(self, addr):
		p = self.protocol(self._wp_state, self._wp_image)
		p.factory = self
		return p

