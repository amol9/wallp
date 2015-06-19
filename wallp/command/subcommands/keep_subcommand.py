import re
from datetime import timedelta
from time import time

from ..subcommand import Subcommand, subcmd
from ...db import GlobalVars
from ..exc import CommandError


class KeepError(Exception):
	pass


class KeepSubcommand(Subcommand):

	@subcmd
	def keep(self, period):
		try:
			exp_period = self.keep_wallpaper(period)
			print('wallpaper will stick for next %s'%exp_period)
		except KeepError as e:
			print(str(e))
			raise CommandError()

	
	def keep_wallpaper(self, period):
		period_map = { 's': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks', 'M': 'months', 'Y': 'years' }
		period_regex = re.compile("(\d{1,3})((s|m|h|d|w|M|Y))")

		match = period_regex.match(period)
		
		if match is None:
			raise KeepError('bad time period: %s'%period)

		num = int(match.group(1))
		if num <= 0:
			raise KeepError('bad time period: %s'%period)
		abbr_period = match.group(2)
		tdarg = {}	

		if abbr_period == 'M':
			tdarg['days'] = 30 * num
		elif abbr_period == 'Y':
			tdarg['days'] = 365 * num
		else:
			tdarg[period_map[abbr_period]] = num

		td = timedelta(**tdarg)
		keep_timeout = int(time()) + td.total_seconds()

		globalvars = GlobalVars()
		globalvars.set('keep_timeout', keep_timeout)

		return '%d %s'%(num, period_map[abbr_period][0 : -1 if num == 1 else None])

