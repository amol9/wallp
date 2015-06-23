from argparse import HelpFormatter, _SubParsersAction, SUPPRESS
import os
import textwrap


class CommandHelpFormatter(HelpFormatter):

	def format_help(self):
		help = self._root_section.format_help()
		#help = self._prog
		if help:
		    help = self._long_break_matcher.sub('\n\n', help)
		    help = help.strip('\n') + '\n'
		    pass
		return help

	
	def _format_usage(self, usage, actions, groups, prefix):
		#print 'fusage'
		#if usage is None and not actions:
			#return self._prog
		help = ''
		optionals = []
		positionals = []
		for action in actions:
			if action.option_strings:
				optionals.append(action)
			else:
				positionals.append(action)



		col1 = 15
		col2 = 45
		
		def format_help_lines(lines):
			help = ''
			first_line = True
			at_least_one_line = False

			for line in lines:
				if first_line:
					help += line
					first_line = False
				else:
					help += '{0:<15}{1}'.format('', line)
				help += os.linesep
				at_least_one_line = True

			if not at_least_one_line:
				help += os.linesep
			return help

		for o in optionals:	#choices, default, help
			opt_help = o.help
			opt_help_lines = []
			if opt_help is not None:
				if len(opt_help) > col2:
					opt_help_lines = textwrap.wrap(opt_help, col2)
				else:
					opt_help_lines = [opt_help]

			choices_lines = []
			if o.choices is not None:
				choices = 'choices: ' + ', '.join(o.choices)

				if len(choices) > col2:
					choices_lines = textwrap.wrap(choices)
				else:
					choices_lines = [choices]

			default_lines = []
			if not o.default in [None, SUPPRESS] :
				#import pdb; pdb.set_trace()
				default_lines = ['default: ' + o.default]

			help += ('{0:<%d}'%(col1)).format(', '.join(o.option_strings))
			
			help += format_help_lines(opt_help_lines + choices_lines + default_lines)

		for p in positionals:
			if p.__class__ == _SubParsersAction:
				#import pdb; pdb.set_trace()
				help += os.linesep + 'subcommands:' + os.linesep
				for subcmd in p.choices.keys():
					help += ('{0:<%d}'%(col1)).format(subcmd)
					subcmd_help = p.choices[subcmd].description
					subcmd_help_lines = []
					if subcmd_help is not None:
						if len(subcmd_help) > col2:
							subcmd_help_lines = textwrap.wrap(subcmd_help, col2)
						else:
							subcmd_help_lines = [subcmd_help]
					help += format_help_lines(subcmd_help_lines)


			else:
				help += p.__class__.__name__

		#_SubparsersAction
		#_StoreAction

		if help == '':
			help = None
		return help


	def _zzz_format_action_invocation(self, action):
		return ''


	def _format_action(self, action):
		return ''

	
	def _zzz_metavar_formatter(self, action, default_metavar):
		if action.metavar is not None:
			result = action.metavar
		elif action.choices is not None:
			choice_strs = [str(choice) for choice in action.choices]
			#result = '{%s}' % ','.join(choice_strs)
			result = os.linesep.join(choice_strs)
		else:
			result = default_metavar

		def format(tuple_size):
			if isinstance(result, tuple):
				return result
			else:
				return (result, ) * tuple_size
		return format


