
from . import DBSession


class Config:
	def __init__(self):
		self._session = DBSession()


	def get(self, name):
		group, name = self.split_name(name)

		result = self._session.query(Setting).filter(Setting.group=group, Setting.name=name)		#exc

		if len(result) == 0:
			raise SettingError('no such setting: %s'%name)
		elif len(result) > 0:
			#do something to correct

		return result[0].value


	def set(self, name, value):
		group, name = self.split_name(name)

		settings = self._session.table(Setting)
		settings.update().where(settings.group=group, settings.name=name).values(settings.value=value)

		#handle errors



	def split_name(self, name):
		parts = name.split('.')
		group = parts[0]
		name = name[len(group) + 1 : ]

		if len(name) < 1:
			raise SettingError('invalid setting name: %s'%name)

		return group, name
	
		
