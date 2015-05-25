import socket
import os
import tempfile
from time import sleep

from .service import Service, ServiceException
from .server.protocol.wallp_client import WallpClient, ImageNone, ImageChanging, ImageAbort
from .server.transport.tcp_connection import TCPConnection, HangUp
from .logger import log


class ServerError(Exception):
	def __init__(self, message, retry=False):
		Exception.__init__(self, message)
		self.retry = retry


class SizeError(ServerError):
	pass


#a class to talk to wallp server
class WallpService(Service):
	def __init__(self):
		self._host = ''
		self._port = 40001
		self._wallp_client = None


	def get_image(self):
		retries = 3
		delay = 10

		while retries > 0:
			try:
				print 'start get_image'
				self.start_connection()

				self.update_frequency()
				if not self.has_image_changed():
					raise ServerImageNotChanged('server image is unchanged')

				self.get_image_from_server()
				retries = 0

				self.close_connection()

			except ServerError as e:
				print e.message
				if e.retry:
					retries -= 1
					sleep(delay)
					delay *= 2
				else:
					raise ServiceException()
			except HangUp as e:
				self._wallp_client.transport = None
				if retries > 0:
					retries -= 1
					sleep(delay)
					delay *= 2
				else:
					raise ServiceException('server hung up')


	def update_frequency(self):
		frequency = self._wallp_client.get_frequency()
		print 'freq', frequency
		#extract frequency and store it, db


	def has_image_changed(self):
		last_change = self._wallp_client.get_last_change()
		print 'last change' , last_change
		#get last change from db and compare

		return True

	
	def start_connection(self):
		if self._wallp_client is None:
			self._wallp_client = WallpClient()

		transport = self._wallp_client.transport
		if transport is not None and not transport.is_closed():
			return 

		print 'starting connection'
		try:
			connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connection.connect((self._host, self._port))

			transport = TCPConnection(connection, self._wallp_client)
			self._wallp_client.makeConnection(transport)
		except socket.error as e:
			log.error(str(e))
			if e.errno == 111:
				raise ServerError('connection refused, server down')


	def is_connection_open(self, connection):
		try:
			connection.fileno()
		except socket.error as e:
			return False

		return True


	def close_connection(self):
		self._wallp_client.close_connection()


	def check_recvd_image_size(self, expected_size, image_path):
		recvd_size = os.stat(image_path).st_size
		if recvd_size != expected_size:
			raise SizeError('received image size mismatch, expected: %d, received: %d'%(expected_size, recvd_size))
		print 'image ok'


	def retry_image(self):
		retries = 3
		delay = 7

		while retries > 0:
			sleep(delay)
			print 'retrying server..'

			try:
				image_gen = self._wallp_client.get_image()
				image_gen.next()
				return image_gen

			except (ImageNone, ImageChanging) as e:
				retries -= 1
				delay *= 2

		raise ServerError('image none or changing on the server for too long')
			

	def get_image_from_server(self):
		extension = None
		length = None
		chunk_count = None

		temp_image_file = tempfile.NamedTemporaryFile()
		image_file = temp_image_file.file

		image_gen = self._wallp_client.get_image()
		success = False

		repeat = True
		while repeat:
			try:
				if not success:
					success = image_gen.next()
				extension, length = image_gen.next()
				print extension, length

				for chunk in image_gen:
					print 'got chunk',
					image_file.write(chunk)

				repeat = False

				image_file.close()
				self.check_recvd_image_size(length, temp_image_file.name)
				#print 'received image'

			except (ImageNone, ImageChanging) as e:
				image_gen = self.retry_image()
				success = True

			except (ImageAbort, SizeError) as e:
				#log str(e)
				if repeat:
					image_gen = self._wallp_client.get_image()
					success = False
					#truncate the file
				else:
					image_file.close()
					os.remove(temp_image_file.name)
					raise ServerError()

		return temp_image_file.name

