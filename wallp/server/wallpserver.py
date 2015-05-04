import socket
import select
import os
from multiprocessing import Process, Pipe

from .scheduler import Scheduler


class WallpServer():
	def __init__(self, port):
		self._port = port


	def start(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.bind(('', self._port))
		server.listen(5)

		os.mkfifo('.wpff')
		fifo = os.open('.wpff', os.O_RDONLY | os.O_NONBLOCK)
		print 'fifo open'

		ilist = [server, fifo]
		olist = []

		scheduler = Scheduler()

		while ilist:
			rlist, wlist, elist = select.select(ilist, olist, ilist)

			for r in rlist:
				if r is server:
					print 'incoming conn'
					conn, client = r.accept()
					data = ''
					while True:
						d = conn.recv(1024)
						if not d:
							break
						data += d
					conn.sendall(self.handle_request(data.strip()))
					conn.close()
				elif r is fifo:
					data = ''
					while True:
						d = os.read(r, 1024)
						if d == '':
							break
						data += d
					if data != '':
						print data
				else:
					print 'bad readable from select'

			if scheduler.is_ready():



	def handle_request(self, command):
		if command == 'frequency':
			return '1h'
		elif command == 'wallp':
			return 'wallpaper-data'
		else:
			return 'bad command'
