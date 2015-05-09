import struct


class Message():
	def __init__(self):
		self.length = None
		self.buffer = ''


class MessageReceiver():
	def __init__(self, blocking=False):
		self._messages = {}
		self._blocking = blocking


	def recv(self, connection):
		message = None

		if not connection in self._messages.keys():
			message = Message()
			self._messages[connection] = message
		else:
			message = self._messages[connection]


		while True:
			data = connection.recv(1024)

			message.buffer += data

			if len(message.buffer) >= 4 and message.length is None:
				message.length = struct.unpack('>i', message.buffer[:4])[0]
				message.buffer = message.buffer[4:]

			if len(message.buffer) > message.length:
				raise Exception()

			elif len(message.buffer) == message.length:
				buffer = message.buffer
				del self._messages[connection]
				return buffer

			if not self._blocking:
				break

		return None


def prefix_message_length(message):
	return struct.pack('>i', len(message)) + message


