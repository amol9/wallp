import os

class ControlPipe():
	def __init__(self, server):
		self._pipe = None

		if exists('.wpff'):
			os.remove('.wpff')

		os.mkfifo('.wpff')
		fifo = os.open('.wpff', os.O_RDONLY | os.O_NONBLOCK)
		print 'fifo open'


	def read_command(self):
		data = ''
		while True:
			d = os.read(self._pipe, 1024)
			if d == '':
				break
			data += d
		if data != '':
			print data

		return data


