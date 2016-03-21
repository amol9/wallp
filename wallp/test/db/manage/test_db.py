from unittest import TestCase, main as ut_main
from os.path import join as joinpath, dirname, abspath, exists
from os import sep

from wallp.db.manage.db import DB
from wallp.globals import Const


class TestDB(TestCase):
	script_location = joinpath(sep.join(dirname(abspath(__file__)).split(sep)[0 : -3]), 'db', 'manage', 'migrate')


	def test_upgrade_to_head(self):
		db = DB()
		db.upgrade(self.script_location, 'test.db', 'head')


	def test_backup(self):
		db = DB()
		dest_path = '.'
		dest_db_path = db.backup(dest_path=dest_path)

		self.assertTrue(exists(dest_db_path))


	def test_upgrade_wallp_db(self):
		db = DB()

		bkp_db_path = db.backup()
		db.upgrade(self.script_location, bkp_db_path, 'head')


if __name__ == '__main__':
	ut_main()

