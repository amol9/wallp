from subprocess import check_output, CalledProcessError
import os

from wallp.logger import log
from mangoutils.system import *

if is_py3():
	from subprocess import DEVNULL
else:
	DEVNULL = open(os.devnull, 'wb')


class command():
	def __init__(self, cmd):
		self._cmd = cmd

	def __enter__(self):
		return self

	def execute(self, supress_output=False):
		try:
			output = None
			if supress_output:
				check_output(self._cmd, shell=True, stderr=DEVNULL)
			else:
				output = check_output(self._cmd, shell=True)
			if is_py3() and not supress_output:
				output = output.decode(encoding='utf-8')

			return output, 0
		except CalledProcessError as e:
			#log.error('error while executing system command, return code: %d'%e.returncode)
			return e.output, e.returncode

	def __exit__(self, exc_typ, exc_val, exc_tb):
		pass

