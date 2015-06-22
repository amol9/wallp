
from ..subcommand import Subcommand, subcmd
from ...util import Scheduler, SchedulerError
from ..exc import CommandError


class ScheduleSubcommand(Subcommand):

	@subcmd
	def schedule(self):
		pass


class ScheduleSubSubcommands(ScheduleSubcommand):

	@subcmd
	def add(self, frequency):
		scheduler = Scheduler()
		try:
			scheduler.set_frequency(frequency)
		except SchedulerError as e:
			print(str(e))
			raise CommandError()


	@subcmd
	def remove(self):
		scheduler = Scheduler()
		scheduler.remove()
		
