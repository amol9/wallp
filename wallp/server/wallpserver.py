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


class WallpServer():
	def __init__(self, port):
		self._port = port
		self._state = 'ready'

		self._ilist = []
		self._olist = []

		self._last_change = None
		self._chunks = {}

		self._clients = []
		self._image_len = None
		self._chunk_size = 100000
		self._image_ext = None
		self._chunk_count = None


	def start(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.bind(('', self._port))
		server.listen(5)

		self._ilist.append(server)

		if exists('.wpff'):
			os.remove('.wpff')

		os.mkfifo('.wpff')
		fifo = os.open('.wpff', os.O_RDONLY | os.O_NONBLOCK)
		print 'fifo open'

		self._ilist.append(fifo)

		scheduler = Scheduler()
		image_path = None
		image_buffer = None
		chunk_count = None

		while self._ilist:
			try:
				rlist, wlist, elist = select.select(self._ilist + self._clients, self._olist,
							self._ilist + self._clients, 0.1)

				for r in rlist:
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
						
					elif r is fifo:
						data = ''
						while True:
							d = os.read(r, 1024)
							if d == '':
								break
							data += d
						if data != '':
							print data
					elif r is inpipe:
						#import pdb; pdb.set_trace()
						image_path = inpipe.recv()
						print "inpipe: ", image_path

						self._ilist.remove(inpipe)
						self._last_change = int(time())
						self._state = 'ready'
						self._image_ext = image_path[image_path.rfind('.') + 1:]
						self._image_len = os.stat(image_path).st_size	#exc

						self._chunk_count = int(self._image_len / self._chunk_size)
						if self._image_len > (self._chunk_count * self._chunk_size):
							self._chunk_count += 1
					else:
						print 'bad readable from select'

				for w in wlist:
					if not w in self._chunks.keys():
						continue

					chunk = self._chunks.get(w, None)

					if chunk is None:
						print 'bad writable from select'

					if image_buffer is None:
						with open(image_path, 'rb') as f:
							image_buffer = f.read()

					print 'sending image chunk to client..'
					response = Response()
					response.type = Response.IMAGE_CHUNK
					response.image_chunk.data = image_buffer[chunk * self._chunk_size : self._chunk_size]

					w.send(response.SerializeToString())
					if chunk + 1 == self._chunk_count:
						w.close()
						del self._chunks[w]
						self._olist.remove(w)

						if len(self._chunks) == 0:
							del image_buffer
					else:
						self._chunks[w] += 1

				if scheduler.is_ready():
					print 'scheduler ready'
					outpipe, inpipe = Pipe()
					try:
						p = Process(target=change_wallpaper, args=(outpipe,))
						p.start()
						self._state = 'in_progress'
					except Exception as e:		#refine exception
						pass

					self._ilist.append(inpipe)
			except socket.error as e:
				print e.strerror
				print e.errno
				import traceback; traceback.print_exc()
				return


	def handle_request(self, request_string, connection):
		response = None
		conn_close = True
		print 'received request'
		command = None
		request = Request()
		request.ParseFromString(request_string)

		print 'request type: ', request.type

		if command == 'frequency':
			response = '1h'

		elif command == 'last_change':
			response = self._last_change

		elif request.type == Request.IMAGE:
			if self._state == 'ready':
				self._olist.append(connection)
				self._chunks[connection] = 0
				'''response = 'image-ext: ' + self._image_ext + '\n\r' +\
						'image-len: ' + str(self._image_len) + '\n\r'''
				response = Response()
				response.type = Request.IMAGE
				#response.image_info = ImageInfo()
				response.image_info.extension = self._image_ext
				response.image_info.length = self._image_len
				response.image_info.chunks = 0

			elif self._state == 'in_progress':
				response = 'in-progress'

			conn_close = False
			self._clients.remove(connection)

		else:
			response = 'bad-command'

		print 'sending response: ', response
		if response is not None:
			connection.send(response.SerializeToString())

		if conn_close:
			self._clients.remove(connection)
			connection.close()


