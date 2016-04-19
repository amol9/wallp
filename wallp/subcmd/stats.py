
from redcmd.api import Subcommand, subcmd, CommandError
from redlib.api.prnt import format_size, ColumnPrinter, Column, ColumnPrinterError, SepColumn

from ..db.app.statistics import Statistics


__all__ = ['StatsSubcommand']


class StatsSubcommand(Subcommand):

	@subcmd
	def stats(self):
		'Print wallpaper statistics.'

		st = Statistics()

		cp = ColumnPrinter(cols=[Column(width=30), SepColumn(), Column(fill=True)])

		cp.printf('wallpaper count', str(st.wallpaper_count))
		cp.printf('usage time', str(st.usage_time))
		cp.printf('avg life of a wallpaper', st.avg_wallpaper_life)
		cp.printf('avg image size', format_size(st.avg_downloaded_image_size))
		cp.printf()

		incp = ColumnPrinter(cols=[Column(width=30), SepColumn(), Column(width=6, align='r')], row_width=38)
		cp.printf('top domains', incp)

		for domain, count in st.top_domains:
			incp.printf(domain, str(count))
		incp.done()


