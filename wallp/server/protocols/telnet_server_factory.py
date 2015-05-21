
from ..imported.twisted.internet_protocol import Factory
from .telnet_server import TelnetServer


class TelnetServerFactory(Factory):
	def __init__(self, server):
		self._server = server


	def buildProtocol(self, addr):
		p = self.protocol(self._server)
		p.factory = self
		return p


