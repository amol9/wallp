
from redcmd.api import commandline_execute


def main():
	from .db.manage.db import DB

	db = DB()
	db.check()

	from .util import log
	from .db.app.config import Config, ConfigError

	config = Config()
	log.start(config.get('client.logfile'), loglevel=config.get('client.loglevel'))

	from .subcmd import all
	from .version import __version__
	from . import const

	commandline_execute(prog=const.app_name, description=const.app_description, version=__version__,
				_to_hyphen=True, default_subcommand='change', moves=True)

