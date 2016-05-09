import sys
from os.path import expanduser

from redcmd.api import execute_commandline


def main():
	from .db.manage.db import DB

	db = DB()
	response = db.check()

	from .util.printer import printer

	response and printer.printf('program maintenance', response)

	from .util import log
	from .db.app.config import Config, ConfigError
	from . import const

	config = Config()
	try:
		log.start(expanduser(config.eget('client.logfile', default=const.logfile)), loglevel=config.eget('client.loglevel', default=40))
	except ConfigError as e:
		print(str(e) + '\nlog start failed')

	from .subcmd import all
	from .version import __version__

	def update_autocomplete_cb():
		printer.printf('program maintenance', 'autocomplete updated')

	execute_commandline(prog=const.app_name, description=const.app_description, version=__version__, _to_hyphen=True, 
			default_subcommand='source random', moves=True, update_autocomplete_cb=update_autocomplete_cb)

