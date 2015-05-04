import socket
import select
import os
from multiprocessing import Process, Pipe
from os.path import exists

from .scheduler import Scheduler
from ..helper import get_image, compute_style
from ..desktop_factory import get_desktop, DesktopException


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


	def start(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.bind(('', self._port))
		server.listen(5)

		if exists('.wpff'):
			os.remove('.wpff')

		os.mkfifo('.wpff')
		fifo = os.open('.wpff', os.O_RDONLY | os.O_NONBLOCK)
		print 'fifo open'

		ilist = [server, fifo]
		olist = []

		scheduler = Scheduler()

		while ilist:
			rlist, wlist, elist = select.select(ilist, olist, ilist, 0.1)

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
				elif r is inpipe:
					#import pdb; pdb.set_trace()
					d = inpipe.recv()
					print "inpipe: ", d
					ilist.remove(inpipe)

				else:
					print 'bad readable from select'

			if scheduler.is_ready():
				print 'scheduler ready'
				outpipe, inpipe = Pipe()
				p = Process(target=change_wallpaper, args=(outpipe,))
				p.start()

				ilist.append(inpipe)


	def handle_request(self, command):
		if command == 'frequency':
			return '1h'
		elif command == 'wallp':
			return 'wallpaper-data'
		else:
			return 'bad command'
