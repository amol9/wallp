
from ..imported.twisted.internet_protocol import Protocol


class Message(Protocol):
	def __init__(self):
		self._buffer = ''


	def messageReceived(self, message):
		raise NotImplemented('needs to be overridden in a subclass')


	def messageError(self, message):
		raise NotImplemented('needs to be overridden in a subclass')


		
