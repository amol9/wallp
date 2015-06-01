
from mutils.system import get_scheduler, FrequencyError, PlatformError

from ..globals import Const


class SchedulerError(Exception):
	pass


class Scheduler:
	def __init__(self):
		try:
			self._sys_scheduler = get_scheduler()
		except PlatformError as e:
			raise SchedulerError('scheduler error: ' + str(e))


	def set_frequency(self, freq):
		if freq is None:
			return

		cmd = Const.scheduler_cmd

		taskname = Const.scheduler_task_name
		if freq == '0':
			if self._sys_scheduler.exists(taskname):
				r = sch.delete(taskname)
				print('schedule deletion %s..'%('succeeded' if r else 'failed'))
			else:
				print('no schedule exists..')
		else:
			if self._sys_scheduler.exists(taskname):
				sch.delete(taskname)

			try:
				r = self._sys_scheduler.schedule(freq, cmd, taskname)
			except FrequencyError as e:
				raise SchedulerError('scheduler error: ' + str(e))

			print('schedule creation %s..'%('succeeded' if r else 'failed'))


