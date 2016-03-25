
from redcmd.api import Subcommand, Arg, CommandError, moved
from asq.initiators import query as asq_query

from ..source.source_factory import SourceFactory


__all__ = ['ChangeSubcommand']


class Target:
	def __init__(self, name, query=True, color=True, subcmd='', src=None):
		self.name	= name
		self.query	= query
		self.color	= color
		self.subcmd	= subcmd
		self.src	= src
		self.base	= ['source']

	
	def match(self, src):
		if self.src is not None:
			return self.src == src
		else:
			return self.name == src


	def args(self, query, color):
		self.base.append(self.name)
		self.base.extend(self.subcmd.split())

		if self.query and query is not None:
			self.base.extend(['-q', query])

		if self.color and color is not None:
			self.base.extend(['-c', color])

		return self.base


class ChangeSubcommand(Subcommand):
	
	@moved	# moved to source subcommands
	def change(self, service=Arg(choices=SourceFactory().source_names, default='random', opt=True), query=None, color=None):
		'''Change the wallpaper.
		service: 	source name to get the wallpaper from
		query: 		search term, specify multiple words by enclosing them in quotes
		color: 		preferred color'''

		targets = [
				Target('google', query=True, color=True),
				Target('imgur', query=True, color=False, subcmd='search'),
				Target('color', query=False, color=True, src='bitmap'),
				Target('bing', query=False, color=False),
				Target('reddit', query=True, color=False),
				Target('deviantart', query=True, color=False),
				Target('favorites', query=False, color=False),
				Target('random', query=False, color=False)
				]

		target = next(iter(asq_query(targets).where(lambda t : t.match(service))), None)
		return target.args(query, color)

