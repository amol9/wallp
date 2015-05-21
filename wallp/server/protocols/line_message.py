
from .message import Message
from ..server_helper import get_limits


#receives simple newline terminated message
class LineMessage(Message):
	def __init__(self):
		Message.__init__(self)


	def dataReceived(self, data):
		self._message += data
		if self._message > get_limits().max_line_message_length:
			self.messageError(self._message)
			self._message = ''

		if self._message.endswith(os.linesep):
			self.messageReceived(self._message[0:-1])
			self._message = ''


	def connectionLost(self, reason=None):
		self._message = ''

