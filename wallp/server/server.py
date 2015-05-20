import socket
import select
import os
from os.path import exists
from time import time
from datetime import timedelta

from .scheduler import Scheduler
from .proto.server_pb2 import Response, ImageInfo, ImageChunk
from .proto.client_pb2 import Request
from .change_wallpaper import ChangeWallpaper, WPState
from .wallpaper_image import WallpaperImage
from .server_helper import ServerStats, ServerSharedData, LinuxLimits
from .transport.tcp_connection import TCPConnection
from .transport.address import Address
from .protocols.wallp_server_factory import WallpServerFactory
from .transport.pipe_connection import PipeConnection


def scheduled_task_placeholder():
	pass


class Server():
	def __init__(self, port):
		self._port = port
		self._server = None
		self._shared_data = ServerSharedData()
		self._limits = LinuxLimits()
		self._stats = ServerStats()


	def start_server_socket(self):
		self._server = self.create_socket(self._port)
		self._shared_data.in_list.append(self._server)

		self._stats.start_time = time()


	def start_telnet_server_socket(self):
		self._telnet_server = self.create_socket(self._port + 1)
		self._shared_data.in_list.append(self._telnet_server)


	def create_socket(self, port):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.bind(('', port))
		server.listen(5)

		return server


	def start_scheduler(self):
		self._scheduler = Scheduler()

		protocol = WPChangeMessage()
		transport = PipeConnection(protocol)

		self._shared_data.in_list.append(transport)
		self._change_wp = ChangeWallpaper(transport)

		#global scheduled_task_placeholder
		#self._scheduler.add_job(scheduled_task_placeholder, '5s', 'change_wallpaper')
		#scheduled_task_placeholder = self._change_wp.execute
		self.setup_job()

		self._scheduler.start()


	def setup_job(self):
		pass


	def start(self):
		self.start_server_socket()
		self.start_telnet_server_socket()
		self.start_scheduler()

		in_list = self._shared_data.in_list
		client_list = self._shared_data.client_list

		wallp_server_factory = WallpServerFactory()
		telnet_server_factory = TelnetServerFactory()

		while len(in_list) > 0 or len(client_list) > 0:
			readable = writeable = exceptions = None
			self._stats.update_clients(len(client_list))

			try:
				readable, writeable, exceptions = select.select(in_list + client_list, \
									client_list, \
									in_list + client_list)

			except TypeError as e:
				#log
				print e.message
				break

			except socket.error as e:
				print 'select error'

				for conn in client_list:
					try:
						fno = conn.fileno()
					except socket.error:

						print 'found dead connection'
						client_list.remove(conn)
						if conn in out_list:
							out_list.remove(conn)

				for conn in out_list:
					try:
						fno = conn.fileno()
					except socket.error:
						print 'found dead connection'
						out_list.remove(conn)

				continue

			except ValueError as e:
				import pdb; pdb.set_trace()

			for r in readable:
				if r is self._change_wp_pipe:
					wp_state = self._change_wp_pipe.recv()

								elif r is self._server:
					print 'incoming connection'
					self.handle_incoming_connection(client_list, wallp_server_factory)
				
				elif r is self._telnet_server:
					print 'incoming telnet connection'
					self.handle_incoming_connection(client_list, telnet_server_factory)

				elif r in client_list:
					try:
						r.doRead()
					except HangUp as e:
						print 'client hung up'
						client_list.remove(r)
						continue
					
				else:
					print 'bad readable from select'

			for w in writeable:
				try:
					w.doWrite()
				except HangUp as e:
					print 'client hung up'
					client_list.remove(w)
					continue

			for e in exceptions:
				print 'select found exceptions'
				pass
				#do something


	def handle_incoming_connection(self, client_list, factory):
		if len(client_list) < self._limits.clients:
			connection, client_address = r.accept()

			addr = Address(client_address)
			protocol = factory.buildProtocol(addr)
			transport = TCPConnection(connection, protocol)
			protocol.makeConnection(transport)

			client_list.append(transport)
		else:
			print 'connections full'



	def cleanup_closed_connections(conn_list):
		pass
		#issue: can't recv() on open connections, it'll remove data from their buffers


	def shutdown(self):
		self._scheduler.shutdown()

