from unittest import TestCase, main as ut_main
from Queue import Queue
import struct

from mayserver.protocol.fixed_length_message import FixedLengthMessage



class TestFixedLengthMessage(TestCase):
	messages = Queue()

	@classmethod
	def setUpClass(cls):
		FixedLengthMessage.messageReceived = lambda self, msg : cls.messages.put(msg)


	@classmethod
	def tearDownClass(cls):
		delattr(FixedLengthMessage, 'messageReceived')


	def tearDown(self):
		while not self.messages.empty():
			self.messages.get()


	def testSinleMessage(self):
		flm = FixedLengthMessage()

		msg = '1234567890'
		data = struct.pack('>i', len(msg)) + msg

		flm.dataReceived(data)

		recvd_msg = self.messages.get()
		self.assertEquals(recvd_msg, msg)
		self.assertTrue(self.messages.empty())


	def testMultipleCompleteMessages(self):
		flm = FixedLengthMessage()

		msg1 = '1234567890'
		msg2 = 'hello server'
		msg3 = '1'

		data = struct.pack('>i', len(msg1)) + msg1 + struct.pack('>i', len(msg2)) + msg2 + struct.pack('>i', len(msg3)) + msg3

		flm.dataReceived(data)

		recvd_msg = self.messages.get()
		self.assertEquals(recvd_msg, msg1)
		recvd_msg = self.messages.get()
		self.assertEquals(recvd_msg, msg2)
		recvd_msg = self.messages.get()
		self.assertEquals(recvd_msg, msg3)

		self.assertTrue(self.messages.empty())


if __name__ == '__main__':
	ut_main()



