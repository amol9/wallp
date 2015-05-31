from unittest import TestCase, main as ut_main

from wallp.db.create_db import create_db


class TestCreateDb(TestCase):
	def test_create_db(self):
		create_db('test.db')

if __name__ == '__main__':
	ut_main()
