from time import time, sleep
import struct

from .fixed_length_message import FixedLengthMessage


class Timeout(Exception):
	pass


class BlockingFixedLengthMessage(FixedLengthMessage):
	def __init__(self):
		FixedLengthMessage.__init__(self)
		self._messages = []


	def receiveMessage(self, timeout=120):
		message = self.getMessage()
		if message is not None:
			return message

		start_time = time()
		while True:
			self.transport.doRead()

			message = self.getMessage()
			if message is not None:
				return message

			if time() - start_time > timeout:
				raise Timeout('receiveMessage timeout')

			sleep(0.1)


	def getMessage(self):
		if len(self._messages) > 0:
			message = self._messages[0]
			del self._messages[0]
			return message


	def messageReceived(self, message):
		self._messages.append(message)


	def sendMessage(self, data):
		message = struct.pack('>i', len(data)) + data
		self.transport.write_blocking(message)

