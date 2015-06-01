from unittest import TestCase, main as ut_main

from wallp.db.create_db import CreateDB


class TestCreateDb(TestCase):
	def test_create_db(self):
		create_db = CreateDB('test.db')
		create_db.create_schema()
		create_db.insert_data()


if __name__ == '__main__':
	ut_main()
