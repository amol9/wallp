import inspect

from .command import Command


def subcmd(func):
	func.subcmd = True
	return func


class SubcmdFunc:
	def __init__(self, subcmd, func, arg_names):
		self.subcmd 	= subcmd
		self.func 	= func
		self.arg_names	= arg_names

	
	def execute(self, args):
		arg_list = [getattr(args, name) for name in self.arg_names]
		self.func(self.subcmd, *arg_list)


class Choices:
	def __init__(self, list, default=None):
		self.list = list
		assert default is None or self.list.index(default) >= 0
		self.default = default

	
class PositionalArg:
	def __init__(self, nargs=None):
		self.nargs = nargs


class Subcommand(Command):
	name = 'subcommand'

	def __init__(self, parser):
		self.parser = parser
		self.subparsers = None
		self.add_subcommands()


	def add_subcommands(self):
		for subcmd_cls in self.__class__.__subclasses__():
			self.add_subcommand(subcmd_cls)


	def add_subcommand(self, subcmd_cls):
		if self.subparsers is None:
			self.subparsers = self.parser.add_subparsers(dest=self.name)
		
		for member_name, member_val in inspect.getmembers(subcmd_cls):
			if inspect.ismethod(member_val):
				func = member_val
				if getattr(func, 'subcmd', None) is not None:
					if not func.__name__ in func.im_class.__dict__.keys():
						continue

					if self.subparsers._name_parser_map.has_key(func.__name__):
						raise SubcommandError('added subcommand %s again'%func.__name__)

					parser = self.subparsers.add_parser(func.__name__)
					subcmd = subcmd_cls(parser)

					argspec = inspect.getargspec(func)
					assert argspec.args[0] == 'self'
					del argspec.args[0]

					#import pdb; pdb.set_trace()

					if argspec.defaults is not None:
						default_offset = len(argspec.args) - len(argspec.defaults)
					else:
						default_offset = len(argspec.args)

					for arg in argspec.args:
						arg_index = argspec.args.index(arg)

						default = None
						names 	= None
						choices = None
						nargs	= None
						if arg_index >= default_offset:
							default = argspec.defaults[arg_index - default_offset]
							names = ['-' + arg[0], '--' + arg]

							if default.__class__ == Choices:
								choices_obj = default
								choices = choices_obj.list
								default = choices_obj.default
								if default is None:
									names = [arg]
							elif default.__class__ == PositionalArg:
								nargs = default.nargs
								default = None
								names = [arg]
	
						else:
							names = [arg]

						kwargs = {
						'default'	: default,
						'choices'	: choices,
						'help'		: func.__doc__
						}

						if nargs is not None:
							kwargs['nargs'] = nargs
						parser.add_argument(*names, **kwargs) 

					print func.__name__
					parser.set_defaults(subcmd_func=SubcmdFunc(subcmd, func, argspec.args))


