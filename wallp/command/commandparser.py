from argparse import ArgumentParser


class CommandParser(ArgumentParser):

	def format_help(self):
		'Copied from argparse. To remove third part and to swap usage and description.'

		formatter = self._get_formatter()

		# description
		formatter.add_text(self.description)

		# usage
		formatter.add_usage(self.usage, self._actions,
				self._mutually_exclusive_groups)


		# positionals, optionals and user-defined groups
		# removed

		# epilog
		formatter.add_text(self.epilog)

		# determine help from format above
		return formatter.format_help()


