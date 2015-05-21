from unittest import TestCase, main as ut_main

from datetime import datetime, timedelta

from wallp.server.server import Server, scheduled_task_placeholder
from wallp.manager import Manager
from wallp.server.scheduler import Scheduler
from apscheduler.jobstores.memory import MemoryJobStore


port = 40001

class TestServer(TestCase):
	@classmethod
	def setUpClass(cls):
		cls._orig_jobstores = Scheduler.jobstores
		Scheduler.jobstores['default'] = MemoryJobStore()


	@classmethod
	def tearDownClass(cls):
		Scheduler.jobstores = cls._orig_jobstores


	def start_server(self, server):
		try:
			server.start()
		except KeyboardInterrupt:
			server.shutdown()

	
	def test_server_start(self):
		self.setup_job_runonce({'seconds': 5})
		server = Server(port)
		self.start_server(server)


	def test_client(self):
		Manager.parse_args = lambda x : None
		Manager.set_frequency = lambda x : None

		cl = Manager()
		cl.get_image_from_wallp_server('localhost,' + str(port))


	def setup_job_interval(self, int_arg):
		def new_setup_job(server_instance):
			global scheduled_task_placeholder
			server_instance._scheduler._apscheduler.add_job(server_instance._change_wp.execute, 'interval', **int_arg)

			print 'added job for test'

		Server.setup_job = new_setup_job


	def setup_job_runonce(self, delta_arg):
		def new_setup_job(server_instance):
			d = datetime.now()
			d += timedelta(**delta_arg)
			global scheduled_task_placeholder
			server_instance._scheduler._apscheduler.add_job(server_instance._change_wp.execute, 'date', run_date=d)

			print 'added job for test'

		Server.setup_job = new_setup_job


if __name__ == '__main__':
	ut_main()

