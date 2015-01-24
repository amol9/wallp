from subprocess import check_output, CalledProcessError, DEVNULL

from wallp.logger import log
from wallp.system import *


class command():
	def __init__(self, cmd):
		self._cmd = cmd

	def __enter__(self):
		return self

	def execute(self, supress_output=False):
		try:
			out = None
			if supress_output:
				out = check_output(self._cmd, shell=True, stderr=DEVNULL)
			else:
				out = check_output(self._cmd, shell=True)
			if is_py3():
				out = out.decode(encoding='utf-8')
			return out
		except CalledProcessError as e:
			#log.error('error while executing system command, return code: %d'%e.returncode)
			return None

	def __exit__(self, exc_typ, exc_val, exc_tb):
		pass

