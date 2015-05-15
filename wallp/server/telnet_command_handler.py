
class TelnetCommandHandler():
	def __init__(self, server):
		self._server = server


	def handle(self, command):
		if command == 'stats':
			response = str(self._server._stats) + '\r'
		else:
			response = 'bad command\n'

		return response

