import socket
import os
from os.path import exists
from time import time

from .select_call import SelectCall, SelectError
from .scheduler import Scheduler
from .change_wallpaper import ChangeWallpaper
from .wallpaper_image import WallpaperImage
from .server_helper import ServerStats, ServerSharedState, LinuxLimits
from .transport.tcp_connection import TCPConnection, HangUp, ConnectionAbort
from .transport.address import Address
from .protocols.wallp_server import WallpServer
from .protocols.telnet_server import TelnetServer
from .protocols.wp_change_message import WPChangeMessage
from .transport.pipe_connection import PipeConnection
from .protocols.wallp_server_factory import WallpServerFactory
from .protocols.telnet_server_factory import TelnetServerFactory
from ..logger import log


def scheduled_task_placeholder():
	pass


class Server():
	def __init__(self, port):
		self._port = port
		self._server = None
		self._shared_data = ServerSharedState()
		self._limits = LinuxLimits()
		self._stats = ServerStats()


	def start_server_socket(self):
		self._server = self.create_socket(self._port)
		#self._shared_data.in_list.append(self._server)

		self._stats.start_time = time()


	def start_telnet_server_socket(self):
		self._telnet_server = self.create_socket(self._port + 1)
		#self._shared_data.in_list.append(self._telnet_server)


	def create_socket(self, port):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.bind(('', port))
		server.listen(5)

		return server


	def start_scheduler(self):
		self._scheduler = Scheduler()

		protocol = WPChangeMessage(self._shared_data)
		transport = PipeConnection(protocol)
		protocol.makeConnection(transport)

		self._shared_data.in_pipes.append(transport.getReadPipe())
		self._change_wp = ChangeWallpaper(transport)

		#global scheduled_task_placeholder
		#self._scheduler.add_job(scheduled_task_placeholder, '5s', 'change_wallpaper')
		#scheduled_task_placeholder = self._change_wp.execute
		self.setup_job()

		self._scheduler.start()


	def start_protocol_factories(self):
		self._wallp_server_factory = WallpServerFactory.forProtocol(WallpServer, self._shared_data)
		self._telnet_server_factory = TelnetServerFactory.forProtocol(TelnetServer, self)


	def setup_job(self):
		pass


	def start(self):
		log.info('starting server...')

		self.start_server_socket()
		self.start_telnet_server_socket()
		self.start_scheduler()
		self.start_protocol_factories()
		self.start_select_loop()


	def start_select_loop(self):
		client_list = self._shared_data.client_list
		in_pipes = self._shared_data.in_pipes
		out_pipes = self._shared_data.out_pipes
		select = SelectCall()
		self._stop_select_loop = False

		while True:
			readable = writeable = exceptions = None
			self._stats.update_clients(len(client_list))

			try:
				readable, writeable, exceptions = select.execute(self.get_in_list(), self.get_out_list())


				self.handle_readable(readable)
				self.handle_writeable(writeable)
				self.handle_exceptions(exceptions)

			except SelectError as e:
				import traceback; traceback.print_exc()
				if e.abort_loop:
					log.error('stopping select loop..')
					break

				self.handle_bad_fds(e.bad_fds)


	def handle_readable(self, readable):
		client_list = self._shared_data.client_list
		in_pipes = self._shared_data.in_pipes

		for r in readable:
			if r is self._server:
				log.debug('incoming wallp client connection')
				self.handle_incoming_connection(r, self._wallp_server_factory)
			
			elif r is self._telnet_server:
				log.debug('incoming telnet client connection')
				self.handle_incoming_connection(r, self._telnet_server_factory)

			elif r in client_list or r in in_pipes:
				try:
					r.doRead()
				except HangUp as e:
					log.error(str(e))
					r.abortConnection(raiseException=False)
					client_list.remove(r)
				
			else:
				log.error('bad readable from select')

	
	def handle_writeable(self, writeable):
		client_list = self._shared_data.client_list	
		for w in writeable:
			if w in client_list:
				try:
					w.doWrite()
				except (HangUp, ConnectionAbort) as e:
					log.error(str(e))
					client_list.remove(w)

			else:
				log.error('bad writable from select')


	def handle_exceptions(self, exceptions):
		if len(exceptions) > 0:
			log.error('select found %d exceptions'%len(exceptions))


	def handle_bad_fds(self, bad_fds):
		if bad_fds is None:
			return

		client_list = self._shared_data.client_list	
		map(client_list.remove, bad_fds)


	def handle_incoming_connection(self, server_socket, factory):
		client_list = self._shared_data.client_list

		if len(client_list) < self._limits.clients:
			connection, client_address = server_socket.accept()
			log.debug('client connected: ' + str(client_address))

			addr = Address(*client_address)
			protocol = factory.buildProtocol(addr)
			transport = TCPConnection(connection, protocol)
			protocol.makeConnection(transport)

			client_list.append(transport)
		else:
			log.error('connections full')


	def get_in_list(self):
		return [self._server] + [self._telnet_server] + self._shared_data.client_list + self._shared_data.in_pipes


	def get_out_list(self):
		return self._shared_data.client_list


	def shutdown(self):
		self._scheduler.shutdown()
		self._stop_select_loop = True

	def pause(self):
		#pause scheduler
		self._stop_select_loop = True

	def resume(self):
		#resume scheduler
		self.start_select_loop()

