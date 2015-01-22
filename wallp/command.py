from subprocess import check_output, CalledProcessError

from wallp.logger import log
from wallp.system import *


class command():
	def __init__(self, cmd):
		self._cmd = cmd

	def __enter__(self):
		return self

	def execute(self):
		try:
			out = check_output(self._cmd, shell=True)
			if is_py3():
				out = out.decode(encoding='utf-8')
			return out
		except CalledProcessError as e:
			log.error('error while scheduling..')

	def __exit__(self, exc_typ, exc_val, exc_tb):
		pass

