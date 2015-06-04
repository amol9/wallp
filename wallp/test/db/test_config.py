from unittest import TestCase, main as ut_main, TestLoader
from functools import partial

from wallp.db import Config, DBSession, Base, SettingError


def cmp_test_case_order(tc1, tc2):
	func1 = getattr(TestConfig, tc1)
	func2 = getattr(TestConfig, tc2)

	return func1.__order__ < func2.__order__

	
TestLoader.sortTestMethodsUsing = cmp_test_case_order


class SettingTestData:
	def __init__(self, fullname, value, vtype, valid_name, group, name):
		self.fullname = fullname
		self.value = value
		self.vtype = vtype
		self.valid_name = valid_name
		self.group = group
		self.name = name


class TestConfig(TestCase):
	dbsession 	= None
	data_inserted 	= False
	settings 	= None

	@classmethod
	def setUpClass(cls):
		cls.dbsession = DBSession(':memory:')
		Base.metadata_createall(cls.dbsession.engine)


	def insert_data(func, *args):
		def new_func(*args):
			instance = args[0]
			assert type(instance) == TestConfig

			if instance.data_inserted:
				return

			split_name = partial(Config.split_name, None)
			for setting in instance.settings:
				group = name = None
				try:
					group, name = split_name(setting.fullname)
				except SettingError:
					continue
				instance.dbsession.add(Setting(group=group, name=name, value=setting.value, type=str(setting.vtype)))

			func(*args)

		return new_func


	def order(func, order):
		func.__order = order
		return func


	@classmethod
	def tearDownClass(cls):
		pass


	def test_split_name(self):
		config = Config()

		for setting in self.settings:
			group = name = None
			if setting.valid_name:
				self.assertEquals(config.split_name(setting.fullname), (setting.group, setting.name))
			else:
				self.assertRaises(config.split_name(setting.fullname), SettingError)


	@order(1)
	@insert_data
	def test_set(self):
		


	@order(2)
	def test_get(self):
		pass
