from zope.interface import implements

from twisted.internet.interfaces import ITCPTransport


class Connection():
	implements(ITCPTransport, IReadWriteDescriptor)

	def __init__(self, ...):
		self._tempDataBuffer = b''
		self._tempDataLen = 0


	def doRead(self):
		pass

	#ref: twisted.internet.abstract.FileDescriptor
	def doWrite(self):
		if self._tempDataLen > 0:
			self.writeSomeData(self._tempDataBuffer)


	#ref: twisted.internet.abstract.FileDescriptor
	def write(self, data):
		self._tempDataBuffer += data
		self._tempDataLen += len(data)


	#ref: twisted.internet.tcp.Connection
	#todo: optimize later
	def writeSomeData(self, data):
		self.socket.send(self._tempDataBuffer)
		self._tempDataBuffer = b''
		self._tempDataLen = 0


	def writeSequence(self, data):
		pass


	def loseConnection(self):
		pass


	def loseWriteConnection(self):
		pass


	def abortConnection(self):
		pass


	def getPeer(self):
		pass


	def getHost(self):
		pass


	def getTcpNoDelay(self):
		pass


	def setTcpNoDelay(self, enabled):
		pass


	def getTcpKeepAlive(self):
		pass


	def setTcpKeepAlive(self):
		pass

