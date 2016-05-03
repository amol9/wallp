
from redlib.api.system import get_scheduler, FrequencyError, PlatformError, frequency_help
from redlib.api.misc import trim_docstring

from .. import const


class SchedulerError(Exception):
	pass


class Scheduler:
	frequency_help = trim_docstring(frequency_help)

	def __init__(self):
		try:
			self._sys_scheduler = get_scheduler()
		except PlatformError as e:
			raise SchedulerError('scheduler error: ' + str(e))


	def set_frequency(self, freq):
		assert type(freq) == str
		if freq is None:
			return

		cmd = const.scheduler_cmdline

		taskname = const.scheduler_task_name
		try:
			self._sys_scheduler.parse(freq)
			if self._sys_scheduler.exists(taskname):
				self._sys_scheduler.delete(taskname)

			r = self._sys_scheduler.schedule(freq, cmd, taskname)
			print('schedule creation %s..'%('succeeded' if r else 'failed'))
		except FrequencyError as e:
			help = trim_docstring(self._sys_scheduler.parse.__doc__)
			raise SchedulerError('scheduler error: ' + str(e) + '\n' + help)


	def remove(self):
		taskname = const.scheduler_task_name
		if self._sys_scheduler.exists(taskname):
			r = self._sys_scheduler.delete(taskname)
			print('schedule deletion %s..'%('succeeded' if r else 'failed'))
		else:
				print('no schedule exists..')

