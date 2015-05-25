import struct

from .message import Message


class FixedLengthMessage(Message):
	def __init__(self):
		Message.__init__(self)
		self._length = None


	def dataReceived(self, data):
		self._buffer += data
		next_message_available = True

		while(next_message_available):

			if len(self._buffer) >= 4 and self._length is None:
				self._length = struct.unpack('>i', self._buffer[:4])[0]
				self._buffer = self._buffer[4:]

			if self._length is not None:
				if len(self._buffer) > self._length:
					self.messageReceived(self._buffer[0 : self._length])
					self._buffer = self._buffer[self._length : ]
					self._length = None

				elif len(self._buffer) == self._length:
					self.messageReceived(self._buffer[0 : self._length])
					self._buffer = b''
					self._length = None
					next_message_available = False

				else:
					next_message_available = False


	def sendMessage(self, data):
		message = struct.pack('>i', len(data)) + data
		self.transport.write(message)
