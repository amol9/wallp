from unittest import TestCase, main as ut_main

from wallp.server.scheduler import Scheduler

class TestScheduler(TestCase):

	def test_simple(self):
		def task():
			print('scheduler test task')
			return 100

		sched = Scheduler()
		#sched.set_task(task)
		sched.add_job(
