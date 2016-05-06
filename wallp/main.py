import sys

from redcmd.api import execute_commandline


def main():
	from .db.manage.db import DB

	db = DB()
	db.check()

	from .util import log
	from .db.app.config import Config, ConfigError

	config = Config()
	try:
		log.start(config.eget('client.logfile', default='stdout'), loglevel=config.eget('client.loglevel', default=40))
	except ConfigError as e:
		print(str(e) + '\nlog start failed')

	from .subcmd import all
	from .version import __version__
	from . import const
	from util.printer import printer

	def update_autocomplete_cb():
		printer.printf('program maintenance', 'updated autocomplete data')

	execute_commandline(prog=const.app_name, description=const.app_description, version=__version__, _to_hyphen=True, 
			default_subcommand='change', moves=True, update_autocomplete_cb=update_autocomplete_cb)

