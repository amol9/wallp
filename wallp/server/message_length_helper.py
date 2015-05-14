import struct


class MessageLengthException(Exception):
	pass


class HangUpException(Exception):
	pass


class Message():
	def __init__(self):
		self.length = None
		self.buffer = ''

	
	def complete(self):
		return self.length == len(self.buffer)


class MessageReceiver():
	def __init__(self, blocking=False):
		self._messages = {}
		self._blocking = blocking


	def recv(self, connection):
		messages = None
		current_message = None

		if not connection in self._messages.keys():
			current_message = Message()
			messages = self._messages[connection] = [current_message]
		else:
			messages = self._messages[connection]
			current_message = messages[-1]

		while True:
			data = connection.recv(1024)

			if len(data) == 0:
				if current_message.buffer is None:
					raise HangUpException()

			current_message.buffer += data

			if len(current_message.buffer) >= 4 and current_message.length is None:
				current_message.length = struct.unpack('>i', current_message.buffer[:4])[0]
				current_message.buffer = current_message.buffer[4:]

			if current_message.length is not None and len(current_message.buffer) > current_message.length:
				next_message = Message()
				next_message.buffer = current_message.buffer[current_message.length:]
				messages.append(next_message)
				
				current_message.buffer = current_message.buffer[0 : current_message.length]

			if len(messages) > 1:
				buffer = messages[0].buffer
				del messages[0]
				return buffer			

			if len(current_message.buffer) == current_message.length:
				buffer = current_message.buffer
				del self._messages[connection]
				return buffer

			if not self._blocking:
				break

		return None


def prefix_message_length(message):
	return struct.pack('>i', len(message)) + message


