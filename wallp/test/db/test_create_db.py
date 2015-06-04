from unittest import TestCase, main as ut_main
import os
from os.path import exists

from wallp.db.create_db import CreateDB


class TestCreateDb(TestCase):
	@classmethod
	def setUpClass(cls):
		if exists('test.db'):
			os.remove('test.db')


	def test_create_db(self):
		create_db = CreateDB('test.db')
		create_db.create_schema()
		create_db.insert_data()
		import pdb; pdb.set_trace()


if __name__ == '__main__':
	ut_main()
