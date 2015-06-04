from unittest import TestCase, main as ut_main, TestLoader
from functools import partial
from csv import reader

from wallp.db import Config, DBSession, Base, SettingError, Setting


def cmp_test_case_order(self, tc1, tc2):
	func1 = getattr(TestConfig, tc1)
	func2 = getattr(TestConfig, tc2)

	if getattr(func1, '__order__', None) is None or getattr(func2, '__order__', None) is None:
		return 0

	return func1.__order__ - func2.__order__

	
TestLoader.sortTestMethodsUsing = cmp_test_case_order


class SettingTestData:
	def __init__(self, fullname, value, vtype, valid_name, group, name, new_value, valid_new_value):
		self.fullname 		= fullname			#always str
		self.value 		= eval(value)			#str / int / float
		self.vtype 		= eval(vtype)			#str / int / float type
		self.valid_name 	= eval(valid_name)		#bool
		self.group 		= group				#always str
		self.name 		= name				#always str
		self.new_value 		= eval(new_value)		#str / int / float
		self.valid_new_value 	= eval(valid_new_value)		#bool


class TestConfig(TestCase):
	dbsession 	= None
	data_inserted 	= False
	settings 	= []

	@classmethod
	def setUpClass(cls):
		cls.dbsession = DBSession('tc.db')
		print 'id', id(cls.dbsession.instance)
		Base.metadata.create_all(cls.dbsession.bind)
		cls.dbsession.commit()

		with open('test_config.csv', 'r') as test_config_csv:
			test_config_csv.readline()
			test_config_csv.readline()
			test_data_reader = reader(test_config_csv)

			for row in test_data_reader:
				if row.count < 8:
					continue
				setting = SettingTestData(*[i.strip() for i in row[0 : 8]])
				cls.settings.append(setting)


	def insert_data(func, *args):
		def new_func(*args):
			instance = args[0]
			assert type(instance) == TestConfig

			if instance.data_inserted:
				return

			config = Config()
			print 'id', id(config._session.instance)
			for setting in instance.settings:
				group = name = None
				try:
					group, name = config.split_name(setting.fullname)
				except SettingError:
					continue
				instance.dbsession.add(Setting(group=group, name=name, value=setting.value, type=str(setting.vtype)[7:-2]))
			instance.dbsession.commit()

			func(*args)

		return new_func


	def order(o):
		def new_dec(func):
			func.__order__ = o
			return func
		return new_dec


	@classmethod
	def tearDownClass(cls):
		pass


	@order(0)
	def test_split_name(self):
		print 'TEST SPLIT'
		config = Config()

		for setting in self.settings:
			group = name = None
			if setting.valid_name:
				self.assertEquals(config.split_name(setting.fullname), (setting.group, setting.name))
			else:
				with self.assertRaises(SettingError) as e:
					config.split_name(setting.fullname)


	@order(1)
	@insert_data
	def test_set(self):
		print 'TEST SET'
		config = Config()

		print 'id', id(config._session)
		for setting in self.settings:
			if setting.valid_name:
				if setting.valid_new_value:
					config.set(setting.fullname, setting.new_value)
				else:
					with self.assertRaises(SettingError) as e:
						config.set(setting.fullname, setting.new_value)


	@order(2)
	def test_get(self):
		print 'TEST GET'
		config = Config()

		for setting in self.settings:
			if setting.valid_name:
				value = config.get(setting.fullname)
				print value, type(value)
				if setting.valid_new_value:
					self.assertEquals(value, setting.new_value)
				else:
					self.assertEquals(value, setting.value)
