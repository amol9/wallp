
from redlib.api.prnt import ColumnPrinter


class Printer:

	def __init__(self, verbosity=3):
		self._cp = ColumnPrinter(cols=[25, 1, 35, 12])
		self._verbosity = verbosity


	def printf(self, msg, data, progress=False, percentage_cb=True, col_cb=False, verbosity=1):
		if verbosity > self._verbosity:
			return

		sep = ''
		if data is not None and data != '':
			sep = ':'

		if not progress:
			self._cp.printf(msg, sep, data, '')
		else:
			cb = self._cp.printf(msg, sep, data, '', progress_col=3, col_cb=col_cb)		# return progress callback and complete functions
			
			progress_cb = cb['progress_cb']

			if percentage_cb:
				cycle = [1]
				def progress_cb2(percentage):
					if percentage >= 0:
						progress = '#' * int(percentage / 10)
					else:
						progress = '#' * cycle[0]
						cycle[0] += 1
						cycle[0] %= 10

					progress_cb(progress)

				cb['progress_cb'] = progress_cb2

			return cb


printer = Printer()

