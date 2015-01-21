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
	def schedule(self, freq):
		pass

	@abstractmethod
	def delete(self):
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
		'm': '0/%d * * * *',
		'h': '0 0/%d * * *',
		'd': '0 0 1/%d * *',
		'w': '0 0 * * 0/%d',
		'M': '0 0 1 1/%d *'
	}


	def schedule(self, freq):
		num, period = self.parse(freq)
		cronstr = self.cron_strings[period]%num
		cmd = '(crontab -l ; echo \"%s\" %s) | crontab'%(cronstr, Const.script_name)
		with command(cmd) as c:
			c.execute()


	def delete(self):
		cmd = 'crontab -l | grep -v %s$ | crontab'%Const.script_name
		with command(cmd) as c:
			c.execute()


class WindowsScheduler(Scheduler):
	period_map = {
		'm': 'MINUTE',
		'h': 'HOURLY',
		'd': 'DAILY',
		'w': 'WEEKLY',
		'M': 'MONTHLY'
	}

	
	def scehdule(self, freq):
		num, period = self.parse(freq)
		schtasks_cmd = 'schtasks /create /tn %s /sc %s /mo %d'%(Const.script_name, period_map[period], num)
		with command(schtasks_cmd) as c:
			c.execute()


	def delete(self):
		schtasks_cmd = 'schtasks /delete /tn %s'%Const.script_name
		with command(schtasks_cmd) as c:
			c.execute()


def get_scheduler():
	if is_linux():
		return LinuxScheduler()
	elif is_windows():
		return WindowsScheduler()
	else:
		Exception('unsupported OS')

