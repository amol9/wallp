import os

from redcmd.api import Subcommand, subcmd, CommandError

from ..util import Scheduler, SchedulerError


__all__ = ['ScheduleSubcommand']


class ScheduleSubcommand(Subcommand):

	@subcmd
	def schedule(self):
		'Commands to schedule changing of wallpaper.'
		pass


class ScheduleSubSubcommands(ScheduleSubcommand):

	@subcmd
	def add(self, frequency):
		'''Add schedule.
		frequency: time frequency for changing wallpaper'''

		scheduler = Scheduler()
		try:
			scheduler.set_frequency(frequency)
		except SchedulerError as e:
			print(str(e))
			raise CommandError()

	add.__extrahelp__ = Scheduler.frequency_help + os.linesep
	add.__extrahelp__ += 'If schedule already exists, it\'ll be overwritten'

	@subcmd
	def remove(self):
		'Remove schedule.'

		scheduler = Scheduler()
		scheduler.remove()
		
