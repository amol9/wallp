import sys

from redlib.api.prnt import ColumnPrinter, Column, ColumnPrinterError, SepColumn, ProgressColumn, Callbacks, terminal_utf8, filter_unicode_chars
from ..db.app.config import Config


class PrinterError(Exception):
	pass


class Printer:

	def __init__(self, verbosity=3):
		self._cp = None
		try:
			self._cp = ColumnPrinter(cols=[Column(width=30), SepColumn(), Column(min=30, fill=True, wrap=True)])
		except ColumnPrinterError as e:
			pass

		self._verbosity = Config().eget('output.verbosity', default=1)


	def printf(self, msg=None, data=None, progress=False, col_updt=False, verbosity=1):
		if verbosity > self._verbosity or sys.stdout is None or not sys.stdout.isatty() or self._cp is None:
			if progress or col_updt:
				return self.empty_callbacks()
			else:
				return

		msg = msg or ''
		data = data or ''

		try:
			if not terminal_utf8():
				msg = filter_unicode_chars(msg)
				data = filter_unicode_chars(data)

			if not progress and not col_updt:
				self._cp.printf(msg, data)
			elif progress:
				try:
					progress_cp = ColumnPrinter(cols=[Column(width=12), ProgressColumn(pwidth=12), Column(width=30)], row_width=55)
					self._cp.printf(msg, progress_cp)
				except ColumnPrinterError as e:
					pass
					return self.empty_callbacks()

				cb = progress_cp.printf('?', '?', '', col_updt=True)

				pcb = cb.progress_cb
				pcp = cb.progress_cp
				cb.progress_cb = lambda p : pcb(1, p)

				def pcp2():
					pcp(1)
					progress_cp.done()
				cb.progress_cp = pcp2

				return cb
			else:
				return self._cp.printf(msg, data, col_updt=True)

		except (UnicodeDecodeError, UnicodeEncodeError) as e:
			log.error(e)


	def empty_callbacks(self):
		cb = Callbacks()
		cb.col_updt_cb = lambda x, y : None
		cb.col_updt_cp = lambda : None
		cb.progress_cb = lambda x : None
		cb.progress_cp = lambda : None
		return cb


printer = Printer()

