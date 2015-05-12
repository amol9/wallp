import struct


class MessageLengthException(Exception):
	pass


class HangUpException(Exception):
	pass


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
			print 'found message'

		while True:
			data = connection.recv(1024)

			if len(data) == 0:
				raise HangUpException()

			message.buffer += data
			print 'received data len, %d'%len(data)
			#import pdb; pdb.set_trace()
			#raw_input()

			if len(message.buffer) >= 4 and message.length is None:
				message.length = struct.unpack('>i', message.buffer[:4])[0]
				print 'message length = %d'%message.length
				message.buffer = message.buffer[4:]

			if message.length is not None and len(message.buffer) > message.length:
				print 'error, message buffer len = %d, message len = %d'%(len(message.buffer), message.length)
				raise MessageLengthException()

			if len(message.buffer) == message.length:
				buffer = message.buffer
				del self._messages[connection]
				return buffer

			if not self._blocking:
				break

		return None


def prefix_message_length(message):
	print 'prefixing msg len, %d'%len(message)
	return struct.pack('>i', len(message)) + message


