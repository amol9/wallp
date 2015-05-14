import socket
import os
import tempfile
from time import sleep

from .proto.client_pb2 import Request
from .proto.server_pb2 import Response
from .server.message_length_helper import MessageReceiver, prefix_message_length, MessageLengthException
from .service import Service, ServiceException


class ServerException(Exception):
	def __init__(self, message, retry=False):
		Exception.__init__(self, message)
		self.retry = retry


class ServerImageNotChanged(ServerException):
	def __init__(self, message):
		ServerException.__init__(self, message, retry=False)


#a class to talk to wallp server
class WallpServer(Service):
	def __init__(self):
		self._host = ''
		self._port = 40001
		self._connection = None


	def get_image(self):
		retries = 3
		delay = 10

		while retries > 0:
			try:
				self.start_connection()

				self.update_frequency()
				if not self.has_image_changed():
					raise ServerImageNotChanged('server image is unchanged')

				self.get_image_from_server()
				retries = 0

				self.close_connection()

			except (ServerException, ServerException, ServerImageNotChanged) as e:
				print e.message
				if e.retry:
					retries -= 1
					sleep(delay)
					delay *= 2
				else:
					raise ServiceException()

	def update_frequency(self):
		request = Request()
		request.type = Request.FREQUENCY

		response = self.send_and_recv(request)

		#extract frequency and store it, db


	def has_image_changed(self):
		request = Request()
		request.type = Request.LAST_CHANGE

		response = self.send_and_recv(request)
		last_change = response.last_change

		#get last change from db and compare

		return True


	
	def start_connection(self):
		if not self.is_connection_open():
			self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._connection.connect((self._host, self._port))
			self._msg_receiver = MessageReceiver(blocking=True)


	def is_connection_open(self):
		if self._connection is None:
			return False

		try:
			self._connection.fileno()
		except socket.error as e:
			return False

		return True

	def close_connection(self):
		self._connection.close()	#exc


	def send_request(self, request):
		self._connection.send(prefix_message_length(request.SerializeToString()))	#exc


	def recv_response(self):
		try:
			message = self._msg_receiver.recv(self._connection)
		except MessageLengthException as e:
			raise ServerException('bad response from server')

		response = Response()
		response.ParseFromString(message)	

		return response


	def get_image_info(self, response):
		extension = response.image_info.extension
		length = response.image_info.length
		chunk_count = response.image_info.chunk_count

		return extension, length, chunk_count	


	def read_image_bytes(self, length, chunk_count):
		response = self.recv_response()
		temp_image_file = tempfile.NamedTemporaryFile()

		image_file = temp_image_file.file

		while chunk_count > 0:
			exception = None

			if response.type == Response.IMAGE_CHUNK:
				chunk = response.image_chunk.data
				image_file.write(chunk)

			elif response.type == Response.IMAGE_ABORT:
				exception = ServerException('server image changed, abort current image; restart', retry=True)

			else:
				exception = ServerException('unexpected response type when expecting image chunk')

			if exception is not None:
				image_file.close()
				os.remove(temp_image_file.name)
				raise exception

			chunk_count -= 1

		image_file.close()
		self.check_recvd_image_size(length, temp_image_file.name)

		return temp_image_file.name


	def check_recvd_image_size(self, expected_size, image_path):
		recvd_size = os.stat(image_path).st_size
		if recvd_size != expected_size:
			os.remove(image_path)
			raise ServerException('received image size mismatch, expected: %d, received: %d'%(expected_size, recvd_size))


	def retry_image(self):
		retries = 3
		sleep_time = 20

		request = Request()
		request.type = Request.IMAGE

		while retries > 0:
			sleep(sleep_time)
			print 'retrying server..'
			response = self.send_and_recv(request)

			if response.type != Response.IMAGE_CHANGING:
				return response

			retries -= 1
			sleep_time *= 2

		raise ServerException('server image is changing for a long time; giving up')


	def get_image_from_server(self):
		extension = None
		length = None
		chunk_count = None

		request = Request()
		request.type = Request.IMAGE
		response = self.send_and_recv(request)

		if response.type == Response.IMAGE_CHANGING:
			response = self.retry_image()

		if response.type == Response.IMAGE_NONE:
			raise ServerException('no image set on server')

		elif response.type == Response.IMAGE_INFO:
			extension, length, chunk_count = self.get_image_info(response)
			temp_image_path = self.read_image_bytes(length, chunk_count)
			print extension, length
			return extension, temp_image_path
			
		else:
			raise ServerException('bad response', retry=True)


	def send_and_recv(self, request, retries=3, delay=2):
		while retries + 1 > 0:
			try:
				self.send_request(request)
				response = self.recv_response()
				return response

			except MessageLengthException:
				print('badly formed message from server, retrying...')
				retries -= 1
				if retries + 1 > 0:
					sleep(delay)
					delay *= 2

		raise ServerException('communication error')
