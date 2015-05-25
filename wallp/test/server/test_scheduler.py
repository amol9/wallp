from unittest import TestCase, main as ut_main
from time import sleep
import os
from os.path import exists
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers import SchedulerAlreadyRunningError, SchedulerNotRunningError

from wallp.server.scheduler import Scheduler


class Task():
	def __init__ (self):
		self.count = 0

	def execute(self):
		print('scheduled task run')
		self.count += 1


def task_placeholder():
	pass


job_db = 'test_jobs.db'


class TestScheduler(TestCase):

	@classmethod
	def setUpClass(cls):
		cls._orig_jobstores = Scheduler.jobstores
		Scheduler.jobstores['default'] = SQLAlchemyJobStore(url='sqlite:///' + job_db) 


	@classmethod
	def tearDownClass(cls):
		Scheduler.jobstores = cls._orig_jobstores

		if exists(job_db):
			os.remove(job_db)


	def test_simple(self):
		sched = Scheduler()
		global task_placeholder

		task = Task()

		sched.add_job(task_placeholder, '3s', 'test_simple')
		task_placeholder = task.execute

		sched.start()
		sleep(4)

		self.assertEquals(1, task.count)

		sched.remove_job('test_simple')

		self.assertFalse(sched.job_exists('test_simple'))

		sched.shutdown()


	def test_full(self):
		sched = Scheduler()
		global task_placeholder
		
		task = Task()
		sched.add_job(task_placeholder, '3s', 'test_full')
		task_placeholder = task.execute

		self.assertTrue(sched.job_exists('test_full'))

		sched.start()
		sleep(3.5)

		self.assertEquals(1, task.count)

		sleep(3.5)

		self.assertEquals(2, task.count)

		sched.shutdown()
		sleep(5)

		sched.start()
		sleep(1)

		self.assertEquals(2, task.count)

		sched.shutdown()


	def test_start_exception(self):
		sched = Scheduler()
		sched.start()

		self.assertRaises(SchedulerAlreadyRunningError, sched.start)
		sched.shutdown()

	
	def test_shutdown_exception(self):
		sched = Scheduler()
		self.assertRaises(SchedulerNotRunningError, sched.shutdown)

		sched.start()
		sched.shutdown()
		self.assertRaises(SchedulerNotRunningError, sched.shutdown)


if __name__ == '__main__':
	ut_main()
