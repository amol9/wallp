from time import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor


class Scheduler():
	jobstores = {
		'default' :SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
	}

	executors = {
		'default': ThreadPoolExecutor(1)
	}

	job_defaults = {
		'coalesce' : True,
		'max_instances' : 1
	}


	def __init__(self):
		self._next_run = time() + 5
		self._apscheduler = BackgroundScheduler(jobstores=self.jobstores, executors=self.executors, job_defaults=self.job_defaults)


	def is_ready(self):
		if time() >= self._next_run:
			self._next_run += 100
			return True
		return False


	def add_job(self, func):
		pass


	def set_task(self, func):
		pass


	def start(self):
		self._apscheduler.start()


	def pause(self):
		pass


	def stop(self):
		pass
