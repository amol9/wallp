from zope.interface import implements

from twisted.internet.interfaces import ITCPTransport, IReadWriteDescriptor


class PipeConnection:
	implements(ITransport, IReadWriteDescriptor)


	def __init__(self, protocol, reactor=None):
		self.rpipe, self.wpipe = os.pipe() 
		self.protocol = protocol

		self._tempDataBuffer = []


	def doRead(self):
		data = self.rpipe.recv()
		self.protocol.dataReceived(data)	#handle multiple messages


	def doWrite(self):
		for data in self._tempDataBuffer:
			self.wpipe.send(data)
			self.remove(data)


	def write(self, data):
		self._tempDataBuffer.append(data)


	def writeSequence(self, data):
		raise NotImplemented('method not implemented')


	def loseConnection(self):
		pass


	def getHost(self):
		pass


	def getPeer(self):
		pass

