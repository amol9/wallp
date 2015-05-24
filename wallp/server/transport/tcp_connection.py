from zope.interface import implements
import socket
from threading import Lock
from time import time

from ..imported.twisted.internet_interfaces import ITCPTransport, IReadWriteDescriptor, IConsumer
from ...logger import log


class HangUp(Exception):
	pass


class ConnectionAbort(Exception):
	pass


plock = Lock()

def socket_call(func, args=()):
	try:
		r = func(*args)
		if func.__name__ == 'recv' and len(r) == 0:
			raise HangUp()

		return r
	except socket.error as e:
		#log.error(str(e))
		#with plock:
			#import traceback; traceback.print_exc()
		if e.errno in [104, 32]:
			raise HangUp()
		elif e.errno in [11]:
			return



class TCPConnection():
	implements(ITCPTransport, IReadWriteDescriptor, IConsumer)

	def __init__(self, socket, protocol):
		self.socket = socket
		self.protocol = protocol
		self._tempDataBuffer = b''
		self._tempDataLen = 0
		self._producer = None
		self._close_after_write_complete = False
		self._start_time = time()


	def doRead(self):
		data = socket_call(self.socket.recv, args=(1024,))
		if data is not None:
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

		if self._tempDataLen == 0 and self._close_after_write_complete:
			self.abortConnection()


	#ref: twisted.internet.abstract.FileDescriptor
	def write(self, data):
		self._tempDataBuffer += data
		self._tempDataLen += len(data)


	#ref: twisted.internet.tcp.Connection
	#todo: optimize later
	def writeSomeData(self, data):
		sent = socket_call(self.socket.send, args=(self._tempDataBuffer,))
		self._tempDataBuffer = self._tempDataBuffer[sent : ]
		self._tempDataLen = len(self._tempDataBuffer)


	def write_blocking(self, data):
		socket_call(self.socket.sendall, args=(data,))


	def writeSequence(self, data):
		pass


	def loseConnection(self):
		pass


	def loseWriteConnection(self):
		pass


	def closeAfterWriteComplete(self):
		self._close_after_write_complete = True


	def shutdownConnection(self):
		socket_call(self.socket.shutdown, args=(socket.SHUT_WR,))


	def abortConnection(self, raiseException=True):
		socket_call(self.socket.close)
		self.socket = None
		if raiseException:
			raise ConnectionAbort('connection closed')


	def get_lifetime(self):
		return time() - self._start_time


	def is_closed(self):
		if self.socket is None:
			return True

		try:
			self.socket.fileno()
		except socket.error as e:
			return True
		return False


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


