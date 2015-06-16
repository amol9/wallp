
from mayloop.imported.twisted.internet_protocol import Factory
from ..protocol.wp_change_message import WPChangeMessage


class WPChangeMessageFactory(Factory):
	protocol = WPChangeMessage

	def __init__(self, wp_state, wp_image):
		self._wp_state = wp_state
		self._wp_image = wp_image


	def buildProtocol(self):
		p = self.protocol(self._wp_state, self._wp_image)
		p.factory = self
		return p

