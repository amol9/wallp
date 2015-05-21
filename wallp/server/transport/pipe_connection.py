from zope.interface import implements
import os

from ..imported.twisted.internet_interfaces import ITransport, IReadWriteDescriptor

class Pipe:
	def __init__(self, pipe, connection):
		self.pipe = pipe
		self.connection = connection


	def fileno(self):
		return self.pipe


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


	def getReadPipe(self):
		return Pipe(self.rpipe, self)


	def getWritePipe(self):
		return Pipe(self.wpipe, self)

