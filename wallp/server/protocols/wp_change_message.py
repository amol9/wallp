from time import time

from ..imported.twisted.internet_protocol import Protocol


class WPState():
	NONE = 0
	READY = 1
	CHANGING = 2


class WPChangeMessage(Protocol):
	def __init__(self, server_shared_state):
		self._server_shared_state = server_shared_state


	def dataReceived(self, data):
		self.messageReceived(data)


	def messageReceived(self, message):
		if message == WPState.READY:
			self._server_shared_state.last_change = int(time())
			self._server_shared_state.wp_state = WPState.READY

			self._server_shared_state.abort_image_producers()
			self._server_shared_state.wp_image.set_path(wp_path)

		elif message == WPState.CHANGING:
			self._server_shared_state.wp_state = WPState.CHANGING

		elif message == WPState.ERROR:
			if self._server_shared_state.wp_image is not None:
				self._server_shared_state.wp_state = WPState.READY
			else:
				self._server_shared_state.wp_state = WPState.NONE
				
		elif type(message) == str:
			if self._server_shared_state.wp_state == WPState.READY:
				print 'wp path: ', message
				self._server_shared_state.wp_image.set_path(message)
			else:
				self.messageError('wallpaper path received when not expected, %s'%message)

		
	def messageError(self, reason):
		#log
		print reason

