from time import time

from mayloop.imported.twisted.internet_protocol import Protocol
from ..wallpaper_image import WPImageError
from ...util.logger import log


class WPState():
	NONE = 0
	READY = 1
	CHANGING = 2
	ERROR = 3

	def __init__(self):
		self.state = self.NONE


class WPChangeMessage(Protocol, object):
	def __init__(self, wp_state, wp_image):
		self._wp_state = wp_state
		self._wp_image = wp_image


	def dataReceived(self, data):
		self.messageReceived(data)


	def messageReceived(self, message):
		if message == WPState.READY:
			log.debug('new image ready')
			#self._server_shared_state.last_change = int(time())
			self._wp_state.state = WPState.READY

			#self._server_shared_state.abort_image_producers() ???

		elif message == WPState.CHANGING:
			self._wp_state.state = WPState.CHANGING

		elif message == WPState.ERROR:
			if self._wp_image is not None:
				self._wp_state.state = WPState.READY
			else:
				self._wp_state.state = WPState.NONE
				
		elif type(message) == str:
			if self._wp_state.state == WPState.READY:
				try:
					self._wp_image.path = message
				except WPImageError as e:
					log.error('error loading new image')
					self._wp_state = WPState.NONE
			else:
				self.messageError('wallpaper path received when not expected, %s'%message)

		
	def messageError(self, reason):
		log.error(reason)

