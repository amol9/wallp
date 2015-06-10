from unittest import TestCase, main as ut_main
from os.path import exists
import logging

from wallp.client import Client, GetImageError
from wallp.service import service_factory
from wallp.db.create_db import CreateDB
from wallp.globals import Const
from wallp.util import log


class TestClient(TestCase):

	@classmethod
	def setUpClass(cls):
		Const.db_path = 'test.db'
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
			

	def get_image(self, service_name):
		client = Client(service_name=service_name)
		try:
			filepath, width, height = client.get_image()
		except GetImageError:
			continue

		self.assertIsNotNone(filepath)
		self.assertTrue(exists(filepath))
		self.assertIsInstance(width, int)
		self.assertIsInstance(height, int)


	def test_bitmap(self):
		spec = CWSpec()
		spec.service_name = 'bitmap'
		get_image(spec)


	def test_bing(self):
		spec = CWSpec()
		spec.service_name = 'bing'
		get_image(spec)


if __name__ == '__main__':
	ut_main()
