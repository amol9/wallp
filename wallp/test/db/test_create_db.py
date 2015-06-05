from unittest import TestCase, main as ut_main
import os
from os.path import exists

from wallp.db.create_db import CreateDB, CreateDBError


class TestCreateDb(TestCase):
	db_path = 'test.db'

	@classmethod
	def setUpClass(cls):
		if exists(cls.db_path):
			os.remove(cls.db_path)


	def test_create_db(self):
		create_db = CreateDB(self.db_path)
		create_db.execute()

		with self.assertRaises(CreateDBError) as e:
			create_db.execute()


if __name__ == '__main__':
	ut_main()
