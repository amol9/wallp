from importlib import import_module
import sys


def update_db():
	args = sys.argv

	if len(args) > 1 and args[1] == 'install':
		wallp_db_config = None
		wallp_db_exc = None
		try:
			wallp_db_config = import_module('wallp.db.config')
			wallp_db_exc = import_module('wallp.db.exc')
		except ImportError as e:
			print(e)
			return
		
		config = wallp_db_config.Config()

		try:
			config.get('style.tiled_size')
		except (wallp_db_config.ConfigError, wallp_db_exc.NotFoundError):
			config.add('style.tiled_size', 100, int)
			config._dbsession.commit()

