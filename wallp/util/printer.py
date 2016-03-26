
from redlib.api.prnt import ColumnPrinter


class Printer:
	progress_col_width = 10

	def __init__(self, verbosity=3):
		self._cp = ColumnPrinter(cols=[25, 1, 50, self.progress_col_width])
		self._verbosity = verbosity


	def printf(self, msg, data, progress=False, percentage_cb=True, col_cb=False, verbosity=1):
		if verbosity > self._verbosity:
			return

		sep = ''
		if data is not None and data != '':
			sep = ':'
		else:
			data = ''

		if not progress and not col_cb:
			self._cp.printf(msg, sep, data, '')
		else:
			cb = self._cp.printf(msg, sep, data, '', progress_col=3, col_cb=col_cb)
			
			progress_cb = cb.progress_cb
			progress_cp = cb.progress_cp

			if percentage_cb:
				cycle = [1]
				def progress_cb2(percentage):
					if percentage >= 0:
						progress = '#' * int(percentage / self.progress_col_width)
					else:
						progress = '#' * cycle[0]
						cycle[0] += 1
						cycle[0] %= self.progress_col_width

					progress_cb(progress)

				def progress_cp2(value=None):
					if value is not None and value == -1:
						progress = '#' * self.progress_col_width
						progress_cb(progress)
						progress_cp()
					else:
						progress_cp(value)

				cb.progress_cb = progress_cb2
				cb.progress_cp = progress_cp2

			return cb


printer = Printer()

