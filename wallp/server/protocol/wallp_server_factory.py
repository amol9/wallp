
from ..imported.twisted.internet_protocol import Factory
from .wallp_server import WallpServer


class WallpServerFactory(Factory):
	def __init__(self, server_shared_state):
		self._server_shared_state = server_shared_state


	def buildProtocol(self, addr):
		p = self.protocol(self._server_shared_state)
		p.factory = self
		return p

