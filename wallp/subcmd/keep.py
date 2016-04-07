import re
from datetime import timedelta
from time import time

from redcmd.api import Subcommand, subcmd, CommandError

from ..db.app.vars import Vars


__all__ = ['KeepSubcommand']


class KeepError(Exception):
	pass


class KeepSubcommand(Subcommand):

	@subcmd
	def keep(self, period):
		'''Keep the wallpaper unchanged for a certain period of time.
		period: time period'''

		try:
			exp_period = self.keep_wallpaper(period)
			print('wallpaper will stick for next %s'%exp_period)
		except KeepError as e:
			print(str(e))
			raise CommandError()

	
	def keep_wallpaper(self, period):
		'''Time period must of the form: {num}{period}
		num: a number in range 1 to 999
		period: s: seconds
			m: minutes
			h: hours
			d: days
			w: weeks
			M: months
			Y: years

		e.g.	1h (1 hour), 1d (1 day), 2w (2 weeks), etc.'''

		period_map = { 's': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks', 'M': 'months', 'Y': 'years' }
		period_regex = re.compile("(\d{1,3})((s|m|h|d|w|M|Y))")

		match = period_regex.match(period)
		
		if match is None:
			raise KeepError('bad time period: %s'%period)

		num = int(match.group(1))
		if num <= 0 :
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
		keep_timeout = int(time() + td.total_seconds())

		vars = Vars()
		vars.eset('keep_timeout', keep_timeout)

		return '%d %s'%(num, period_map[abbr_period][0 : -1 if num == 1 else None])

	keep.__extrahelp__ = keep_wallpaper.__doc__

