from zope.interface import implements

from ..imported.twisted.internet_interfaces import ITCPTransport, IReadWriteDescriptor, IConsumer


class HangUp(Exception):
	pass


class ConnectionAbort(Exception):
	pass


class TCPConnection():
	implements(ITCPTransport, IReadWriteDescriptor, IConsumer)

	def __init__(self, socket, protocol):
		self.socket = socket
		self.protocol = protocol
		self._tempDataBuffer = b''
		self._tempDataLen = 0
		self._producer = None
		self._close_after_write_complete = False


	def doRead(self):
		data = self.socket.recv(1024)
		if len(data) == 0:
			raise HangUp()

		self.protocol.dataReceived(data)


	#ref: twisted.internet.abstract.FileDescriptor
	def doWrite(self):
		if self._tempDataLen > 0:
			self.writeSomeData(self._tempDataBuffer)

		elif self._producer is not None:
			if self._producer.producing:
				self._producer.resumeProducing()
			else:
				self._producer = None

		elif self._close_after_write_complete:
			self.abortConnection()


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


	def closeAfterWriteComplete(self):
		self._close_after_write_complete = True

	def abortConnection(self):
		self.socket.close()
		self.socket = None
		raise ConnectionAbort('connection closed')


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


	def registerProducer(self, producer, streaming=False):
		if not self._producer:
			self._producer = producer
		else:
			raise Exception('trying to add producer when a producer is already registered')


	def unregisterProducer(self):
		if self._producer is not None:
			self._producer.stopProducing()
			self._producer = None


	def fileno(self):
		return self.socket.fileno()


