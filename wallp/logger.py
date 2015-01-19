import logging
import sys


class Logger():
	def __init__(self, stdout=False, logfile=None, log_testresults=False):
		self._log = logging.getLogger('wallp')
		self._log.propagate = False

		if stdout:
			logst = logging.StreamHandler(sys.stdout)
			logst.setLevel(logging.DEBUG)
			self._log.addHandler(logst)
		
		if logfile:
			logfh = logging.FileHandler(logfile)
			logfh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
			logfh.setLevel(logging.INFO)
			self._log.addHandler(logfh)
	
		self._log.setLevel(logging.DEBUG)

		self._log_testresults = log_testresults

		return


	def debug(self, msg):
		self._log.debug(msg)


	def info(self, msg):
		self._log.info(msg)


	def warning(self, msg):
		self._log.warning(msg)


	def error(self, msg):
		self._log.error(msg)


	def testresult(self, result):
		if self._log_testresults:
			self._testresult.append(result)


	def get_testresult(self):
		if self._log_testresults:
			return self._testresult
		else:
			raise Exception('test result logging is disabled')

	
	def clear_testresult(self):
		self._testresult = []


log = Logger(stdout=True)
