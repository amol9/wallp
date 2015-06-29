import os
import re
from zope.interface import Interface, Attribute, implementer
from sqlalchemy.exc import OperationalError

from .dbsession import DBSession
from .regex import Regex
from .exc import NotFoundError
from ..util import log


class NameError(Exception):
	nv_typename = 'name'

	def __init__(self, fullname):
		Exception.__init__(self, 'no such ' + self.nv_typename + ' ' +  fullname)


class INameValueSet(Interface):
	nvtype 		= Attribute('set type: Setting / Var')
	name_err_type 	= Attribute('exception type to be thrown upon invalid name')

	def add(fullname, value, vtype):
		'Add to set.'

	def get(fullname):
		'Get value from name.'

	def set(fullname, value):
		'Set value.'

@implementer(INameValueSet)
class NameValueSet(object):
	group_regex 	= Regex('[a-zA-Z].*|^$', 'must start with a letter')
	name_regex 	= Regex('[a-zA-Z].*', 'must start with a letter')
	name_err_type	= NameError

	def __init__(self):
		super(NameValueSet, self).__init__()
		self._dbsession = DBSession()
		self._group_max_len = self.nvtype.group.property.columns[0].type.length
		self._name_max_len = self.nvtype.name.property.columns[0].type.length


	def add(self, fullname, value, vtype):
		group, name = self.split_name(fullname)

		if type(vtype) == type:
			vtype = vtype.__name__

		namevalue = self.nvtype(group=group, name=name, value=value, type=vtype)
		self._dbsession.add(namevalue)


	def get(self, fullname):
		namevalue = self.get_namevalue(fullname)

		if namevalue.value is None:
			return None

		vtype = eval(namevalue.type)

		value = None
		if vtype == bool:
			value = bool(eval(namevalue.value))	#fix for bool
		else:
			value = namevalue.value

		return vtype(value)


	def single_result(self, result):
		'A single row of result expected.'

		if len(result) == 0 :
			raise NotFoundError()
		elif len(result) > 0 :
			#do something to correct
			pass

		return result[0]


	def get_namevalue(self, fullname):
		group, name = self.split_name(fullname)

		result = None
		try:
			result = self._dbsession.query(self.nvtype).filter(self.nvtype.group == group, self.nvtype.name == name).all()
		except OperationalError as e:
			log.error(e.orig)
			raise NotFoundError('%s %s not found'%(fullname, self.name_err_type.nv_typename))

		namevalue = None
		try:
			namevalue = self.single_result(result)
		except NotFoundError:
			raise self.name_err_type(fullname)

		return namevalue


	def get_all_names(self):
		result = None
		try:
			result = self._dbsession.query(self.nvtype).all()
		except OperationalError as e:
			log.error(e.orig)
			raise NotFoundError()

		names = []
		for r in result:
			names.append(r.group + '.' + r.name)

		return names

	names = property(get_all_names)


	def set(self, fullname, value):
		namevalue = self.get_namevalue(fullname)
		vtype = eval(namevalue.type)

		if value is not None and type(value) != vtype:
			try:
				if vtype == bool:
					if value.lower() in ['true', 'yes']:
						value = True
					elif value.lower() in ['false', 'no']:
						value = False
					else:
						raise ValueError('use true/false or yes/no')
				else:
					value = vtype(value)
			except ValueError as e:
				raise e 
				#ValueError('value type does not match, expected: %s, got: %s'%(namevalue.type, type(value).__name__))

		namevalue.value = value	
		self._dbsession.commit()


	def split_name(self, name):
		parts = name.split('.')
		if len(parts) == 1 :
			group = ''
			name = parts[0]
		else:
			group = parts[0]
			name = name[len(group) + 1 : ]

		exc_msg = []
		try:
			self.validate(group, max_len=self._group_max_len, regex=self.group_regex)
		except ValueError as e:
			exc_msg.append('group \'%s\' '%group + str(e))

		try:
			self.validate(name, min_len=1, max_len=self._name_max_len, regex=self.name_regex)
		except ValueError as e:
			exc_msg.append('name \'%s\' '%name + str(e))

		if len(exc_msg) > 0 :
			raise ValueError(os.linesep.join(exc_msg))

		return group, name
	

	def validate(self, value, min_len=None, max_len=None, regex=None):
		if min_len is not None and len(value) < min_len:
			raise ValueError('too short, must be at least %d char long'%min_len)

		if max_len is not None and len(value) > max_len:
			raise ValueError('too long, max length = %d'%max_len)

		c_regex = re.compile(regex.expression)

		if c_regex.match(value) is None:
			raise ValueError(regex.err_msg)

