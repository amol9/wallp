import os

from ..subcommand import Subcommand, subcmd
from ...util import Scheduler, SchedulerError
from ..exc import CommandError


class ScheduleSubcommand(Subcommand):

	@subcmd
	def schedule(self):
		'help: commands to schedule changing of wallpaper'
		pass


class ScheduleSubSubcommands(ScheduleSubcommand):

	@subcmd
	def add(self, frequency):
		'''help: add schedule.
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
		'help: remove schedule.'

		scheduler = Scheduler()
		scheduler.remove()
		
