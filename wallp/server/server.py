import socket
import select
import os
from multiprocessing import Process, Pipe
from os.path import exists
from time import time

from .scheduler import Scheduler
from ..helper import get_image, compute_style
from ..desktop_factory import get_desktop, DesktopException
from ..proto.server_pb2 import Response, ImageInfo, ImageChunk
from ..proto.client_pb2 import Request


def change_wallpaper(outpipe):
	print 'changing wallpaper'
	try:
		wp_path = get_image(service_name='bitmap', query=None, color=None)
		print 'wp_path:', wp_path

		style = compute_style(wp_path)

		dt = get_desktop()
		dt.set_wallpaper(wp_path, style=style)

		outpipe.send(wp_path)
		return
	
	except DesktopException:
		#log.error('cannot change wallpaper')
		pass

	outpipe.send('error')


class ServerSharedData():
	def __init__(self):
		self.in = []
		self.out = []
		self.state = None
		self.image_out = {}

		self.clients = []
		self.last_change = None


class Server():
	def __init__(self, port):
		self._port = port
		#self._state = 'ready'

		#self._ilist = []
		#self._olist = []

		'''self._last_change = None
		self._chunks = {}

		self._clients = []
		self._image_len = None
		self._chunk_size = 100000
		self._image_ext = None
		self._chunk_count = None'''

		self._server = None
		self._shared_data = ServerSharedData()


	def start_server_socket(self):
		self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._server.setblocking(0)
		self._server.bind(('', self._port))
		self._server.listen(5)

		self._shared_data.in.append(self._server)


	def start_scheduler(self):
		self._scheduer = Scheduler()
		self._scheduler.start()


	def start_control_pipe(self):
		self._control_pipe = ControlPipe(self)
		self._shared_data.in.append(self._control_pipe.pipe)


	def start(self):
		self.start_server_socket()
		self.start_scheduler()

		while self._ilist:
			try:
				readable, writeable, elist = select.select(self._ilist + self._clients, self._olist,
							self._ilist + self._clients, 0.1)

				for r in readable:
					if r is server:
						print 'incoming conn'
						conn, client = r.accept()
						self._clients.append(conn)

					elif r in self._clients:
						data = ''
						#import pdb; pdb.set_trace()
						while not data.endswith('\n\r'):
							ch = r.recv(1024)
							if not ch or len(ch) == 0:
								break
							data += ch
							print 'reading...'
						self.handle_request(data[0:-2], r)

						#new:
						client_request = ClientRequest(data, self._shared_data)
						response, is_image_response = client_request.process()

						if response is not None:
							self._shared_data.out_buffer[r] = response

							if is_image_response:
								self._shared_data.image_out[r] = ImageResponse(self._shared_data.wp_image)
						
					elif r is self._control_pipe.pipe:
						self._control_pipe.read_command()

					elif r is inpipe:
						#import pdb; pdb.set_trace()
						image_path = inpipe.recv()
						print "inpipe: ", image_path

						self._ilist.remove(inpipe)
						self._last_change = int(time())
						self._state = 'ready'
					else:
						print 'bad readable from select'

				for w in writeable:
					if w in self._shared_data.out_buffer.keys():
						w.send(self._shared_data.out_buffer[w])
						del self._shared_data.out_buffer[w]

						if not w in self._shared_data.image_out.keys():
							w.close()

					elif w in self._shared_data.image_out.keys():
					
					#chunk = self._chunks.get(w, None)
					image_response = self._shared_data.image_out[w]

					#if chunk is None:
						#print 'bad writable from select'

					print 'sending image chunk to client..'
					chunk, last_chunk = image_response.get_next_chunk()
					w.send(chunk)

					if last_chunk:
						del self._shared_data.image_out[w]
						w.close()
						#remove ???

			except socket.error as e:
				print e.strerror
				print e.errno
				import traceback; traceback.print_exc()
				return

