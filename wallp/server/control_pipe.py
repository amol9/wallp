import os
from os.path import exists


class ControlPipe():
	def __init__(self, server):
		self._pipe = None

		if exists('.wpff'):
			os.remove('.wpff')

		os.mkfifo('.wpff')
		self._pipe = os.open('.wpff', os.O_RDONLY | os.O_NONBLOCK)
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


	def get_pipe(self):
		return self._pipe


	pipe = property(get_pipe)


