from time import time

from ..imported.twisted.internet_protocol import Protocol
from ..wallpaper_image import WPImageError
from ...logger import log


class WPState():
	NONE = 0
	READY = 1
	CHANGING = 2
	ERROR = 3


class WPChangeMessage(Protocol, object):
	def __init__(self, server_shared_state):
		self._server_shared_state = server_shared_state


	def dataReceived(self, data):
		self.messageReceived(data)


	def messageReceived(self, message):
		if message == WPState.READY:
			log.debug('new image ready')
			self._server_shared_state.last_change = int(time())
			self.server_wp_state = WPState.READY

			self._server_shared_state.abort_image_producers()

		elif message == WPState.CHANGING:
			self.server_wp_state = WPState.CHANGING

		elif message == WPState.ERROR:
			if self._server_shared_state.wp_image is not None:
				self.server_wp_state = WPState.READY
			else:
				self.server_wp_state = WPState.NONE
				
		elif type(message) == str:
			if self.server_wp_state == WPState.READY:
				try:
					self._server_shared_state.wp_image.path = message
				except WPImageError as e:
					log.error('error loading new image')
					self.server_wp_state = WPState.NONE
			else:
				self.messageError('wallpaper path received when not expected, %s'%message)

		
	def messageError(self, reason):
		log.error(reason)


	def get_server_wp_state(self):
		return self._server_shared_state.wp_state


	def set_server_wp_state(self, value):
		self._server_shared_state.wp_state = value


	server_wp_state = property(get_server_wp_state, set_server_wp_state)

