

class Address:
	def __init__(self, host, port):
		self.host = host
		self.port = port


	def __repr__(self):
		return self.host + ':' + str(self.port)

