
from redcmd.api import subcmd, IntArg

from .base import SourceSubcommand
from ...source.reddit import RedditParams


__all__ = ['RedditSubcommand']


class RedditSubcommand(SourceSubcommand):

	@subcmd
	def reddit(self, query=None, subreddit=None, posts_limit=IntArg(opt=True, default=None, max=100, min=10)):
		'''reddit.com

		run "wallp list colors" to see a list of all supported colors'''

		rp = RedditParams(query=query, subreddit=subreddit, limit=posts_limit)
		self.change_wallpaper(rp)

