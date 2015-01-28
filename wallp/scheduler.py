from abc import ABCMeta, abstractmethod
from subprocess import check_output, CalledProcessError
import re
import os

from wallp.system import *
from wallp.globals import Const
from wallp.logger import log
from wallp.command import command


help = 	'm: minute, h: hour, d: day, w: week, M: month' + os.linesep +\
	'e.g. 1h: every 1 hour, 10m: every 10 minutes, etc.'


class Scheduler():
	__metaclass__ = ABCMeta

	@abstractmethod
	def schedule(self, freq, cmd, taskname):
		pass

	@abstractmethod
	def delete(self, taskname):
		pass

	@abstractmethod
	def exists(self, taskname):
		pass

	def parse(self, freq):
		freq_regex = re.compile("(\d{1,3})((m|h|d|w|M))")
		match = freq_regex.match(freq)

		if match is None:
			raise Exception('time frequency not supported')

		num = match.group(1)
		period = match.group(2)

		return int(num), period


class LinuxScheduler(Scheduler):
	cron_strings = {
		'm': '*/%d * * * *',
		'h': '0 */%d * * *',
		'd': '0 0 */%d * *',
		'w': '0 0 * * */%d',
		'M': '0 0 1 */%d *'
	}


	def schedule(self, freq, cmd, taskname):
		num, period = self.parse(freq)
		cronstr = self.cron_strings[period]%num
		sh_cmd = '(crontab -l ; echo \"%s\" %s \\#%s) | crontab'%(cronstr, cmd, taskname)
		with command(sh_cmd) as c:
			_, rc = c.execute(supress_output=True)
			if rc == 0:
				return True
		return False


	def delete(self, taskname):
		sh_cmd = 'crontab -l | grep -v %s$ | crontab'%taskname
		with command(sh_cmd) as c:
			_, rc = c.execute(supress_output=True)
			if rc == 0:
				return True
		return False

	
	def exists(self, taskname):
		sh_cmd = 'crontab -l | grep -v %s$'%taskname
		with command(sh_cmd) as c:
			_, rc = c.execute(supress_output=True)
			if rc == 0:
				return True
		return False
	


class WindowsScheduler(Scheduler):
	period_map = {
		'm': 'MINUTE',
		'h': 'HOURLY',
		'd': 'DAILY',
		'w': 'WEEKLY',
		'M': 'MONTHLY'
	}

	
	def schedule(self, freq, cmd, taskname):
		num, period = self.parse(freq)
		schtasks_cmd = 'schtasks /create /tn %s /tr \"%s\" /sc %s /mo %d'%\
				(taskname, cmd, self.period_map[period], num)
		log.debug('schedule command: %s'%schtasks_cmd)
		with command(schtasks_cmd) as c:
			_, rc = c.execute(supress_output=True)
			if rc == 0:
				return True
		return False


	def delete(self, taskname):
		out = None	
		schtasks_cmd = 'schtasks /delete /tn %s /f'%taskname
		with command(schtasks_cmd) as c:
			_, rc = c.execute(supress_output=True)
			if rc == 0:
				return True
		return False
				
				
	def exists(self, taskname):
		out = None
		query_cmd = 'schtasks /query /tn %s'%taskname
		with command(query_cmd) as c:
			_, rc = c.execute(supress_output=True)
			if rc == 0:
				return True
		return False


def get_scheduler():
	if is_linux():
		return LinuxScheduler()
	elif is_windows():
		return WindowsScheduler()
	else:
		Exception('unsupported OS')

