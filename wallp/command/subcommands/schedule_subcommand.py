
from ..subcommand import Subcommand, subcmd
from ..util import Scheduler, SchedulerError


class ScheduleSubcommand(Subcommand):

	@subcmd
	def schedule(self, frequency):
		scheduler = Scheduler()
		try:
			scheduler.set_frequency(frequency)
		except SchedulerError as e:
			print(str(e))
			raise AppError()

