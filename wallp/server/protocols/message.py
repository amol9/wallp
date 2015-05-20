
from twisted.internet.protcols import Protocol		#temp import


class Message(Protocol):
	def __init__(self):
		self._message = ''


	def messageReceived(self, message):
		raise NotImplemented('needs to be overridden in a subclass')


	def messageError(self, message):
		raise NotImplemented('needs to be overridden in a subclass')


		
