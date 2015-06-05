import os
import re

from . import DBSession, Setting


class SettingError(Exception):
	pass


class Regex:
	def __init__(self, expr, err_msg):
		self.expression = expr
		self.err_msg = err_msg


class Config:
	group_regex = Regex('[a-zA-Z].*|^$', 'must start with a letter')
	name_regex = Regex('[a-zA-Z].*', 'must start with a letter')

	def __init__(self):
		self._session = DBSession()
		self._group_max_len = Setting.group.property.columns[0].type.length
		self._name_max_len = Setting.name.property.columns[0].type.length


	def add(self, fullname, value, vtype):
		group, name = self.split_name(fullname)

		if type(vtype) == type:
			vtype = str(vtype)[7 : -2]	#e.g. "<type 'int'>" - extract the "int" part

		setting = Setting(group=group, name=name, value=value, type=vtype)
		self._session.add(setting)


	def get(self, name):
		setting = self.get_setting(name)
		vtype = eval(setting.type)

		value = None
		if vtype != str:
			value = eval(setting.value)
		else:
			value = setting.value

		return value


	def single_result(self, result):
		'A single row of result expected.'

		if len(result) == 0:
			raise SettingError('no such setting')
		elif len(result) > 0:
			#do something to correct
			pass

		return result[0]


	def get_setting(self, name):
		group, name = self.split_name(name)

		result = self._session.query(Setting).filter(Setting.group == group, Setting.name == name).all()
		setting = self.single_result(result)

		return setting


	def set(self, name, value):
		setting = self.get_setting(name)
		vtype = eval(setting.type)

		if type(value) != vtype:
			try:
				value = vtype(value)
			except ValueError as e:
				raise SettingError('value type does not match, expected: %s, got: %s'%(setting.type, type(value)))

		setting.value = value
		
		self._session.commit()


	def split_name(self, name):
		parts = name.split('.')
		if len(parts) == 1:
			group = ''
			name = parts[0]
		else:
			group = parts[0]
			name = name[len(group) + 1 : ]

		exc_msg = []
		try:
			self.validate(group, max_len=self._group_max_len, regex=self.group_regex)
		except SettingError as e:
			exc_msg.append('group \'%s\' '%group + str(e))

		try:
			self.validate(name, min_len=1, max_len=self._name_max_len, regex=self.name_regex)
		except SettingError as e:
			exc_msg.append('name \'%s\' '%name + str(e))

		if len(exc_msg) > 0:
			raise SettingError(os.linesep.join(exc_msg))

		return group, name
	

	def validate(self, value, min_len=None, max_len=None, regex=None):
		if min_len is not None and len(value) < min_len:
			raise SettingError('too short, must be at least %d char long'%min_len)

		if max_len is not None and len(value) > max_len:
			raise SettingError('too long, max length = %d'%max_len)

		c_regex = re.compile(regex.expression)

		if c_regex.match(value) is None:
			raise SettingError(regex.err_msg)

