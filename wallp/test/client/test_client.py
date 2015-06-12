from unittest import TestCase, main as ut_main
from os.path import exists
import logging
from time import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wallp.client import Client, GetImageError, KeepError 
from wallp.service import service_factory
from wallp.db import Var
from wallp.db.create_db import CreateDB
from wallp.globals import Const
from wallp.util import log


class TestClient(TestCase):
	db_path = 'test.db'

	@classmethod
	def setUpClass(cls):
		Const.db_path = cls.db_path
		create_db = CreateDB()
		create_db.execute()

		log.start('stdout', logging.DEBUG)


	@classmethod
	def tearDownClass(cls):
		pass


	def test_all_service(self):
		#import pdb; pdb.set_trace()
		for service_type in service_factory.get_all():
			print('testing ' + service_type.name)
			self.get_image(service_type.name)
			

	def get_image(self, service_name):
		client = Client(service_name=service_name)
		try:
			filepath, width, height = client.get_image()
		except GetImageError:
			return

		self.assertIsNotNone(filepath)
		self.assertTrue(exists(filepath))
		self.assertIsInstance(width, int)
		self.assertIsInstance(height, int)


	def test_bitmap(self):
		self.get_image('bitmap')


	def test_bing(self):
		self.get_image('bing')


	def test_deviantart(self):
		self.get_image('deviantart')


	def test_reddit(self):
		self.get_image('reddit')


	def test_google(self):
		self.get_image('google')


	def test_imgur(self):
		self.get_image('imgur')


	def get_new_dbsession(self):
		engine = create_engine('sqlite:///' + self.db_path, echo=Const.debug)
		session_class = sessionmaker(bind=engine)
		return session_class()


	def test_keep_wallpaper(self):
		client = Client()
		now = int(time())
		client.keep_wallpaper('2h')

		dbsession2 = self.get_new_dbsession()
		keep_timeout = dbsession2.query(Var).filter(Var.name == 'keep_timeout').all()[0].value
		self.assertIsNotNone(keep_timeout)
		keep_timeout = int(keep_timeout)

		self.assertGreaterEqual(keep_timeout - now, 2 * 60 * 60)
		self.assertTrue(client.keep_timeout_not_expired())

		client.keep_wallpaper('1d')
		keep_timeout = int(dbsession2.query(Var).filter(Var.name == 'keep_timeout').all()[0].value)

		self.assertGreaterEqual(keep_timeout - now, 24 * 60 * 60)

		try:
			client.keep_wallpaper('15m')
			client.keep_wallpaper('15s')
			client.keep_wallpaper('1Y')
			client.keep_wallpaper('2w')
			client.keep_wallpaper('1M')
		except KeepError as e:
			self.fail(str(e))

		self.assertRaises(KeepError, client.keep_wallpaper, 'm')
		self.assertRaises(KeepError, client.keep_wallpaper, '10')
		self.assertRaises(KeepError, client.keep_wallpaper, '')
		self.assertRaises(KeepError, client.keep_wallpaper, '1000d')
		self.assertRaises(KeepError, client.keep_wallpaper, 'mxxxxxxyyyyyyy')
		self.assertRaises(KeepError, client.keep_wallpaper, 'sm')


if __name__ == '__main__':
	ut_main()
