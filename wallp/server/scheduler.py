from time import time
import re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers import SchedulerAlreadyRunningError, SchedulerNotRunningError

from .. import const
from ..util.logger import log


class Scheduler():
	jobstores = {
		'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
	}

	executors = {
		'default': ThreadPoolExecutor(1)
	}

	job_defaults = {
		'coalesce' : True,
		'max_instances' : 1
	}

	periods = {
		's': 'second',
		'm': 'minute',
		'h': 'hour',
		'd': 'day',
		'w': 'week',
		'M': 'month'
	}


	def __init__(self):
		self._apscheduler = BackgroundScheduler(jobstores=self.jobstores, 
						executors=self.executors, job_defaults=self.job_defaults)


	def parse_frequency(self, freq):
		freq_regex = re.compile("(\d{1,3})((s|m|h|d|w|M))")
		match = freq_regex.match(freq)

		if match is None:
			raise FrequencyException('time frequency not supported')

		num = match.group(1)
		period = match.group(2)

		return int(num), period


	def get_cron_kwarg(self, num, period):
		return {self.periods[period]: '*/%d'%num}


	def add_job(self, func, freq, job_id, args=None):
		num, period = self.parse_frequency(freq)
		cron_kwarg = self.get_cron_kwarg(num, period)

		self._apscheduler.add_job(func, 'cron', id=job_id, args=args, **cron_kwarg)


	def remove_job(self, job_id):
		self._apscheduler.remove_job(job_id)


	def job_exists(self, job_id):
		jobs = self._apscheduler.get_jobs()
		return any([job.id == job_id for job in jobs])


	def start(self):
		try:
			self._apscheduler.start()
		except SchedulerAlreadyRunningError as e:
			log.error(str(e))


	def pause(self):
		self.shutdown()


	def shutdown(self):
		try:
			self._apscheduler.shutdown()
		except SchedulerNotRunningError as e:
			log.error(str(e))

