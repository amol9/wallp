import socket
import os
from os.path import exists
from time import time

from .select_call import SelectCall, SelectError
from .scheduler import Scheduler
from .change_wallpaper import ChangeWallpaper
from .wallpaper_image import WallpaperImage
from .server_helper import ServerStats, ServerSharedState, LinuxLimits, StartError
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
		self._shared_state = ServerSharedState()
		self._limits = LinuxLimits()
		self._stats = ServerStats()


	def start_server_socket(self):
		self._server = self.create_socket(self._port)
		#self._shared_state.in_list.append(self._server)

		self._stats.start_time = time()


	def start_telnet_server_socket(self):
		self._telnet_server = self.create_socket(self._port + 1)
		#self._shared_state.in_list.append(self._telnet_server)


	def create_socket(self, port):
		try:
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.setblocking(0)
			server.bind(('', port))
			server.listen(5)

			return server
		except socket.error as e:
			if e.errno == 98:
				msg = 'address %s:%d already in use'%('', port)
				log.error(msg)
				raise StartError(msg)


	def start_scheduler(self):
		self._scheduler = Scheduler()

		protocol = WPChangeMessage(self._shared_state)
		transport = PipeConnection(protocol)
		protocol.makeConnection(transport)

		self._shared_state.in_pipes.append(transport.getReadPipe())
		self._change_wp = ChangeWallpaper(transport)

		#global scheduled_task_placeholder
		#self._scheduler.add_job(scheduled_task_placeholder, '5s', 'change_wallpaper')
		#scheduled_task_placeholder = self._change_wp.execute
		self.setup_job()

		self._scheduler.start()


	def start_protocol_factories(self):
		self._wallp_server_factory = WallpServerFactory.forProtocol(WallpServer, self._shared_state)
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
		select = SelectCall()
		self._pause_server = False

		while True:
			readable = writeable = exceptions = None
			self._stats.update_clients(len(self.client_list))

			try:
				readable, writeable, exceptions = select.execute(self.get_in_list(), self.get_out_list())


				self.handle_readable(readable)
				self.handle_writeable(writeable)
				self.handle_exceptions(exceptions)

			except SelectError as e:
				if e.abort_loop:
					log.error('stopping select loop..')
					break

				self.handle_bad_fds(e.bad_fds)


	def handle_readable(self, readable):
		for r in readable:
			if r in [self._server, self._telnet_server]:
				self.handle_incoming_connection(r)
			
			elif r in self.client_list or r in self.telnet_client_list or r in self.in_pipes:
				self.transport_call(r.doRead)
				
			else:
				log.error('bad readable from select')

	
	def handle_writeable(self, writeable):
		for w in writeable:
			if w in self.client_list or w in self.telnet_client_list:
				self.transport_call(w.doWrite)

			else:
				log.error('bad writable from select')


	def transport_call(self, func):
		t = func.im_self

		try:
			func()
		except (HangUp, ConnectionAbort) as e:
			log.error(str(e))

			if not isinstance(e, ConnectionAbort):
				t.abortConnection(raiseException=False)

			if isinstance(t.protocol, WallpServer):
				self._stats.update_client_lifetime(t.get_lifetime())
				self.client_list.remove(t)

			elif isinstance(t.protocol, TelnetServer):
				self.telnet_client_list.remove(t)

			elif isinstance(t, ChildPipe):
				self.in_pipes.remove(t)

			else:
				log.error('should not get here, unknown type of transport was closed')


	def handle_exceptions(self, exceptions):
		if len(exceptions) > 0:
			log.error('select found %d exceptions'%len(exceptions))


	def handle_bad_fds(self, bad_fds):
		if bad_fds is None:
			return

		client_list = self._shared_state.client_list	
		map(client_list.remove, bad_fds)


	def handle_incoming_connection(self, server):
		if server is self._server:
			factory = self._wallp_server_factory
			clist = self.client_list

		elif server is self._telnet_server:
			factory = self._telnet_server_factory
			clist = self.telnet_client_list

		else:
			log.error('got an incoming on an unexpected server socket')
			return

		if not self.server_full():
			connection, client_address = server.accept()
			log.debug('client connected: ' + str(client_address))

			addr = Address(*client_address)
			protocol = factory.buildProtocol(addr)
			transport = TCPConnection(connection, protocol)
			protocol.makeConnection(transport)

			clist.append(transport)
		else:
			log.error('connections full')


	def server_full(self):
		return False


	def get_in_list(self):
		wallp_server = [self._server] + self.client_list + self.in_pipes
		telnet_server = [self._telnet_server] + self.telnet_client_list
		return (wallp_server if not self._pause_server else []) + telnet_server


	def get_out_list(self):
		return (self.client_list if not self._pause_server else []) + self.telnet_client_list



	def get_client_list(self):
		return self._shared_state.client_list


	def get_telnet_client_list(self):
		return self._shared_state.telnet_client_list


	def get_in_pipes(self):
		return self._shared_state.in_pipes


	def stop(self):
		self._scheduler.shutdown()
		self._pause_server = True

		for c in self.client_list:
			self.transport_call(c.abortConnection)
		self._server.close()
		self._server = None


	def hot_start(self):
		self.start_server_socket()
		self._pause_server = False
		self._scheduler.start()


	def pause(self):
		self._scheduler.pause()
		self._pause_server = True


	def resume(self):
		self._scheduler.start()
		self.start_select_loop()


	client_list 		= property(get_client_list)
	telnet_client_list 	= property(get_telnet_client_list)
	in_pipes		= property(get_in_pipes)


