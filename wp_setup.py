from importlib import import_module
import sys


def update_db():
	args = sys.argv

	print 'update db call'
	if len(args) > 1 and args[1] == 'install':
		wallp_db_manage_db = None
		wallp_db_exc = None
		try:
			wallp_db_manage_db = import_module('wallp.db.manage.db')
			wallp_db_exc = import_module('wallp.db.exc')
		except ImportError as e:
			print(e)
			return
		
		db = wallp_db_manage_db.DB()
		print('updating db...')

		try:
			db.backup()
			db.upgrade()
			db.insert_data()
		except Exception as e:
			print(e)
		
