from itertools import izip_longest

from .namevalueset import NameValueSet


class NVShortcutError(Exception):
	pass


class NVShortcut:
	def __init__(self, names, defaults, sep, get_only, print_fmt):
		if not get_only and len(names) != len(defaults):
			raise NVShortcutError('number of names and default values do not match')

		self.names = names
		self.defaults = defaults
		self.sep = sep

		self.get_only = get_only
		self.print_fmt = print_fmt


class NVShortcutMixin(object):
	def __init__(self):
		super(NVShortcutMixin, self).__init__()
		self._shortcuts = {}

	
	def add_shortcut(self, shortcut, names, defaults, sep, get_only=False, print_fmt=False):
		self._shortcuts[shortcut] = NVShortcut(names, defaults, sep, get_only=get_only, print_fmt=print_fmt)


	def get(self, name):
		if name in self._shortcuts.keys():

			shortcut = self._shortcuts[name]
			values = []
			for name in shortcut.names:
				value = NameValueSet.get(self, name)
				values.append(value)

			if shortcut.print_fmt:
				output = ''
				for i in range(len(shortcut.names)):
					output += '{0:<25}: {1}'.format(shortcut.names[i], values[i])
					output += shortcut.sep if i != len(shortcut.names) - 1 else ''
				print(output)
				return ''
			else:
				return shortcut.sep.join([str(v) for v in values])

		else:
			return NameValueSet.get(self, name)


	def set(self, name, value):
		if name in self._shortcuts.keys():

			shortcut = self._shortcuts[name]
			if shortcut.get_only:
				raise NVShortcutError('%s is a read only shortcut'%name)

			values = value.split(shortcut.sep)
			if len(values) > len(shortcut.names):
				raise ShortcutError('number of values > number of names')

			for name, value in izip_longest(shortcut.names, values):
				if value is None:
					value = shortcut.defaults[shortcut.names.index(name)]
				NameValueSet.set(self, name, value)

		else:
			NameValueSet.set(self, name, value)

