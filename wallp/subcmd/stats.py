
from redcmd.api import Subcommand, subcmd, CommandError
from redlib.api.prnt import format_size

from ..db.app.statistics import Statistics


__all__ = ['StatsSubcommand']


class StatsSubcommand(Subcommand):

	@subcmd
	def stats(self):
		st = Statistics()

		print 'wallpaper count:', st.wallpaper_count
		print 'top domains:'
		for domain, count in st.top_domains:
			print domain + '\t\t' + str(count)

		print ''
		print 'usage time:', st.usage_time
		print 'avg time for a wallpaper:', st.usage_time / st.wallpaper_count
		print 'avg image size:', format_size(st.avg_downloaded_image_size)

