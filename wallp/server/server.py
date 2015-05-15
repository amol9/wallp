import socket
import select
import os
from multiprocessing import Process, Pipe
from os.path import exists
from time import time
from datetime import timedelta

from .scheduler import Scheduler
from ..proto.server_pb2 import Response, ImageInfo, ImageChunk
from ..proto.client_pb2 import Request
from .message_length_helper import MessageReceiver, prefix_message_length, HangUpException
from .change_wallpaper import ChangeWallpaper, WPState
from .control_pipe import ControlPipe
from .client_request import ClientRequest
from .image_response import ImageResponse
from .wallpaper_image import WallpaperImage
from .telnet_command_handler import TelnetCommandHandler


class ServerStats():
	def __init__(self):
		self.peak_clients = 0
		self.start_time = None
		self.current_clients = 0


	def update_clients(self, count):
		if self.peak_clients < count:
			self.peak_clients = count
		self.current_clients = count


	def __repr__(self):
		repr = ''
		repr += 'peak clients: %d\n'%self.peak_clients
		repr += 'live clients: %d\n'%self.current_clients
		repr += 'uptime: %s'%(str(timedelta(seconds=(int(time() - self.start_time)))))

		return repr



class LinuxLimits():
	def __init__(self):
		self.select = 1024
		self.clients = 1014


class ServerSharedData():
	def __init__(self):
		self.in_list = []
		self.out_list = []
		self.image_out = {}
		self.out_buffers = {}

		self.client_list = []
		self.last_change = None
		self.wp_image = WallpaperImage()
		self.wp_state = WPState.NONE


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

		self._change_wp_pipe, outpipe = Pipe()
		self._shared_data.in_list.append(self._change_wp_pipe)
		self._change_wp = ChangeWallpaper(outpipe)

		#global scheduled_task_placeholder
		#self._scheduler.add_job(scheduled_task_placeholder, '5s', 'change_wallpaper')
		#scheduled_task_placeholder = self._change_wp.execute
		self.setup_job()

		self._scheduler.start()


	def setup_job(self):
		pass


	def start_control_pipe(self):
		self._control_pipe = ControlPipe(self)
		self._shared_data.in_list.append(self._control_pipe.pipe)


	def start(self):
		self.start_server_socket()
		self.start_telnet_server_socket()
		self.start_scheduler()
		self.start_control_pipe()

		in_list = self._shared_data.in_list
		out_list = self._shared_data.out_list
		client_list = self._shared_data.client_list
		telnet_client_list = []
		msg_receiver = MessageReceiver()
		telnet_cmd_handler = TelnetCommandHandler(self)

		while len(in_list) > 0 or len(client_list) > 0:
			readable = writeable = exceptions = None
			self._stats.update_clients(len(client_list))

			try:
				readable, writeable, exceptions = select.select(in_list + client_list + telnet_client_list, \
									out_list + telnet_client_list, \
									in_list + client_list + out_list, 0.1)

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

					if wp_state == WPState.READY:
						self._last_change = int(time())

						for image_response in self._shared_data.image_out.values():
							image_response.abort()

						self._shared_data.wp_state = WPState.READY
						wp_path = self._change_wp_pipe.recv()
						print 'wp_path: ', wp_path
						self._shared_data.wp_image.set_path(wp_path)

						#self._scheduler.remove_job('change_wallpaper')

					elif wp_state == WPState.CHANGING:
						self._shared_data.wp_state = WPState.CHANGING

					else:
						print 'bad wp state'
				elif r is self._server:
					print 'incoming connection'
					if len(set(client_list + out_list)) < self._limits.clients:
						connection, client_address = r.accept()
						client_list.append(connection)
					else:
						print 'connections full'

				elif r is self._telnet_server:
					print 'incoming telnet connection'
					connection, client_address = r.accept()
					telnet_client_list.append(connection)

				elif r in telnet_client_list:
					data = r.recv(1024)
					print 'telnet command: %s'%data
					res = telnet_cmd_handler.handle(data.strip())
					r.send(res)

				elif r in client_list:
					message = None
					try:
						message = msg_receiver.recv(r)

					except HangUpException as e:
						print 'client hung up'
						client_list.remove(r)
						continue

					if message is not None:
					#new:
						client_request = ClientRequest(message, self._shared_data)
						response, is_image_response, keep_alive = client_request.process()

						if response is not None:
							self._shared_data.out_buffers[r] = (response, keep_alive)

							if is_image_response:
								self._shared_data.image_out[r] = ImageResponse(self._shared_data.wp_image)

							if r not in out_list:
								out_list.append(r)

						if not keep_alive:
							print 'removing client'
							client_list.remove(r)	
							print 'len client_list: %d'%len(client_list)

				elif r is self._control_pipe.pipe:
					self._control_pipe.read_command()

				else:
					print 'bad readable from select'

			for w in writeable:
				if w in self._shared_data.out_buffers.keys():
					print 'len out list: %d'%len(out_list)
					w.send(prefix_message_length(self._shared_data.out_buffers[w][0]))

					if not w in self._shared_data.image_out.keys():
						if not self._shared_data.out_buffers[w][1]:
							print 'closing connection'
							w.close()
							out_list.remove(w)
							print 'len out_list: %d'%len(out_list)

					del self._shared_data.out_buffers[w]

				elif w in self._shared_data.image_out.keys():
					image_response = self._shared_data.image_out[w]

					print 'sending image chunk to client..'
					chunk, last_chunk = image_response.get_next_chunk()

					w.send(prefix_message_length(chunk))

					if last_chunk:
						del self._shared_data.image_out[w]
						w.close()
						out_list.remove(w)

			for e in exceptions:
				print 'select found exceptions'
				pass
				#do something


			'''except socket.error as e:
				print e.strerror
				print e.errno
				import traceback; traceback.print_exc()
				return'''

	def cleanup_closed_connections(conn_list):
		pass
		#issue: can't recv() on open connections, it'll remove data from their buffers


	def shutdown(self):
		self._scheduler.shutdown()

