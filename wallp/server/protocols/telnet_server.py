import os

from line_message import LineMessage


class TelnetServer(LineMessage):
	def __init__(self, server):
		LineMessage.__init__(self)
		self._server = server
	

	def messageReceived(self, message):
		if message == 'stats':
			response = str(self._server._stats)
		elif message == '':
			return
		else:
			response = 'bad command'

		self.sendMessage(response + os.linesep)


	def sendMessage(self, message):
		self.transport.write(message)