from time import time, sleep

from .fixed_length_message import FixedLengthMessage


class Timeout(Exception):
	pass


class BlockingFixedLengthMessage(FixedLengthMessage):
	def __init__(self):
		FixedLengthMessage.__init__(self)
		self._message = None


	def receiveMessage(self, timeout=120):
		start_time = time()
		while True:
			self.transport.doRead()

			if self._message is not None:
				message = self._message
				self._message = None
				return message

			if time() - start_time > timeout:
				raise Timeout('receiveMessage timeout')

			sleep(0.1)


	def messageReceived(self, message):
		self._message = message


	def sendMessage(self, data):
		message = struct.pack('>i', len(data)) + data
		self.transport.writeSomeData(message)

