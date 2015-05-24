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
from .transport.pipe_connection import PipeConnection, ChildPipe
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
		self._stats.start_time = time()


	def start_telnet_server_socket(self):
		self._telnet_server = self.create_socket(self._port + 1)


	def create_socket(self, port):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.bind(('', port))
		server.listen(5)

		return server


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
		client_list 		= self._shared_state.client_list
		in_pipes 		= self._shared_state.in_pipes
		out_pipes 		= self._shared_state.out_pipes
		select 			= SelectCall()
		self._pause_server 	= False

		while True:
			readable = writeable = exceptions = None
			self._stats.update_clients(len(client_list))
			self._stats.update_open_fds()

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
		client_list = self._shared_state.client_list
		telnet_client_list = self._shared_state.telnet_client_list
		in_pipes = self._shared_state.in_pipes

		for r in readable:
			if r in [self._server, self._telnet_server]:
				self.handle_incoming_connection(r)
			
			elif (r in client_list) or (r in telnet_client_list) or (r in in_pipes):
				if r in client_list: 
					print 'client read', id(r)
				elif r in in_pipes: print 'pipe read'

				self.transport_call(r.doRead)

			else:
				log.error('bad readable from select')


	def transport_call(self, func):
		client_list = self._shared_state.client_list
		telnet_client_list = self._shared_state.telnet_client_list
		in_pipes = self._shared_state.in_pipes
		t = func.im_self

		try:
			func()
		except (HangUp, ConnectionAbort) as e:
			log.error(str(e))

			if not isinstance(e, ConnectionAbort):
				t.abortConnection(raiseException=False)

			if isinstance(t.protocol, WallpServer):
				self._stats.update_client_lifetime(t.get_lifetime())
				client_list.remove(t)
				print 'client removed from list', len(client_list)

			elif isinstance(t.protocol, TelnetServer):
				telnet_client_list.remove(t)

			elif isinstance(t, ChildPipe):
				in_pipes.remove(t)

			else:
				log.error('should not get here, unknown type of transport was closed')

	
	def handle_writeable(self, writeable):
		client_list = self._shared_state.client_list
		telnet_client_list = self._shared_state.telnet_client_list

		for w in writeable:
			print 'w client list len', len(client_list)
			if (w in client_list) or (w in telnet_client_list):
				self.transport_call(w.doWrite)

			else:
				log.error('bad writable from select')


	def handle_exceptions(self, exceptions):
		if len(exceptions) > 0:
			log.error('select found %d exceptions'%len(exceptions))


	def handle_bad_fds(self, bad_fds):
		if bad_fds is None:
			return

		client_list = self._shared_state.client_list	
		map(client_list.remove, bad_fds)


	def handle_incoming_connection(self, server_socket):
		if server_socket is self._server:
			factory = self._wallp_server_factory
			clist = self._shared_state.client_list

		elif server_socket is self._telnet_server:
			factory = self._telnet_server_factory
			clist = self._shared_state.telnet_client_list

		else:
			log.error('something went wrong, incoming connection not on server or telnet port')
			return

		if not self.server_full():
			connection, client_address = server_socket.accept()
			log.debug('client connected: ' + str(client_address))
			connection.setblocking(0)

			addr = Address(*client_address)
			protocol = factory.buildProtocol(addr)
			transport = TCPConnection(connection, protocol)
			protocol.makeConnection(transport)

			print 'client tr id:', id(transport)
			clist.append(transport)
		else:
			log.error('connections full')

	
	def server_full(self):
		return False


	def get_in_list(self):
		in_list = [self._server] + [self._telnet_server] + self._shared_state.client_list + \
				self._shared_state.telnet_client_list + self._shared_state.in_pipes
		#in_list =  [self._telnet_server] + self._shared_state.telnet_client_list
		#if not self._pause_server:
			#in_list += [self._server] + self._shared_state.client_list + self._shared_state.in_pipes

		return in_list


	def get_out_list(self):
		out_list = self._shared_state.telnet_client_list
		if not self._pause_server:
			out_list += self._shared_state.client_list

		return out_list


	def shutdown(self):
		self._scheduler.shutdown()
		self._pause_server = True


	def pause(self):
		#pause scheduler
		self._pause_server = True


	def resume(self):
		#resume scheduler
		self._pause_server = False

