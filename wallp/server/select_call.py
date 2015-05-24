import select
import socket

from ..logger import log


class SelectError(Exception):
	def __init__(self, message=None, abort_loop=False, bad_fds=None):
		Exception.__init__(self, message)
		self.abort_loop = abort_loop
		self.bad_fds = bad_fds


class SelectCall:
	'wraps calls to select'

	def __init__(self):
		pass


	def execute(self, in_list, out_list):
		readable = writeable = exceptions = None

		try:
			readable, writeable, exceptions = select.select(in_list, out_list, in_list + out_list)

		except TypeError as e:
			log.error(str(e))
			raise SelectError(abort_loop=True)

		except socket.error as e:
			log.error('select socket error\n' + str(e))
			
			bad_fds = []
			for fd in list(set(in_list + out_list)):
				try:
					fd.fileno()
				except socket.error:
					bad_fds.append(fd)

			raise SelectError(bad_fds=bad_fds)

		except ValueError as e:
			log.error(str(e))
			raise SelectError(abort_loop=True)

		return readable, writeable, exceptions

