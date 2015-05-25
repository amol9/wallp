from Queue import Queue


class MockTransport:
	def __init__(self):
		self.messages = Queue()
		self.unregistered = False
		self.producer = None
	

	def write(self, message):
		self.messages.put(message)


	def unregisterProducer(self):
		self.unregistered = True


	def registerProducer(self, producer, streaming=False):
		self.producer = producer


	def closeAfterWriteComplete(self):
		pass

