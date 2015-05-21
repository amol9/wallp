import struct

from .message import Message


class FixedLengthMessage(Message):
	def __init__(self):
		Message.__init__(self)
		self._length = None


	def dataReceived(self, data):
		self._message += data
		next_message_avaialable = True

		while(next_message_avaialable):

			if len(self._message) >= 4 and self._length is None:
				self._length = struct.unpack('>i', self._message[:4])[0]
				self._message = self._message[4:]

			if self._length is not None:
				if len(self._message) > self._length:
					self.messageReceived(self._message[0 : self._length])
					self._message = self._message[self._length : ]
					self._length = None

				elif len(self._message) == self._length:
					self.messageReceived(self._message[0 : self._length])
					self._message = b''
					self._length = None
					next_message_avaialable = False

				else:
					next_message_avaialable = False


	def sendMessage(self, data):
		message = struct.pack('>i', len(data)) + data
		self.transport.write(message)
