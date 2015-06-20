import os

from mutils.system import Scheduler

from ..db import Config, func as dbfunc, GlobalVars, DBError, NotFoundError, ConfigError
from ..db.create_db import CreateDB
from ..util import log, Scheduler, SchedulerError
from .info_printer import InfoPrinter
from ..globals import Const
from .client import Client, ChangeWPError, KeepError


class AppError(Exception):
	pass


class Subcommands(object):
	def __init__(self):
		self._args = None
		self.first_run()


	def set_args(self, args):
		self._args = args

	args = property(None, set_args)	



	def add_config_shortcuts(self):
		config = Config()
		config.add_shortcut('server', ['server.host', 'server.port'], [None, Const.default_server_port], ':')

		setting_names = config.names
		config.add_shortcut('all', setting_names, None, os.linesep, get_only=True, print_fmt=True)


	def change(self):
		args = self._args
		client = Client(service_name=args.service, query=args.query, color=args.color)
		try:
			client.change_wallpaper()
		except ChangeWPError as e:
			log.error(str(e))
			raise AppError()


	def schedule(self):
		scheduler = Scheduler()
		try:
			scheduler.set_frequency(self._args.frequency)
		except SchedulerError as e:
			print(str(e))
			raise AppError()


	def log(self):
		config = Config()
		config.set('client.logfile', self._args.filename)
		config.set('client.loglevel', log.levels[self._args.level])


	def set(self):
		config = Config()
		self.config_call(config.set, self._args.name, self._args.value)


	def get(self):
		config = Config()
		value = self.config_call(config.get, self._args.name)
		print(value)


	def config_call(self, func, *args):
		try:
			r = func(*args)
			return r
		except ConfigError as e:
			print(str(e))
			raise AppError()


	def get_item_list(self):
		item_list = [l for l in dbfunc.get_lists() if l.name == self._args.list_name]
		if len(item_list) == 0:
			raise AppError('%s is not a valid list'%self._args.list_name)
		elif len(item_list) > 1:
			raise AppErrpr('too many lists named %s, something is very wrong'%self._args.list_name)
		return item_list[0]()


	def itemlist_call(self, func, *args, **kwargs):
		try:
			func(*args, **kwargs)
		except (ValueError, NotFoundError) as e:
			print(str(e))
			raise AppError()


	def add(self):
		item_list = self.get_item_list()
		self.itemlist_call(item_list.add, self._args.item, True, commit=True)
		print('%s added to %s list'%(self._args.item, item_list.name))


	def enable(self):
		item_list = self.get_item_list()
		self.itemlist_call(item_list.enable, self._args.item)
		print('%s enabled in %s list'%(self._args.item, item_list.name))


	def disable(self):
		item_list = self.get_item_list()
		self.itemlist_call(item_list.disable, self._args.item)
		print('%s disabled in %s list'%(self._args.item, item_list.name))


	def like(self):
		self.score_call(dbfunc.like_wallpaper)
		

	def dislike(self):
		self.score_call(dbfunc.dislike_wallpaper)


	def score_call(self, func):
		try:
			score = func()
			print('image score: %d'%score)
		except LikeError as e:
			print(str(e))
			raise AppError()



	def keep(self):
		client = Client()
		try:
			exp_period = client.keep_wallpaper(self._args.period)
			print('wallpaper will stick for next %s'%exp_period)
		except KeepError as e:
			print(str(e))
			raise AppError()


	def info(self):
		ip = InfoPrinter(None)
		ip.print_info()


	def db_reset(self):
		choice = raw_input('Are you sure you want to reset the db? [y/N]:')
		if choice == 'y':
			db_path = Const.db_path
			os.remove(db_path)
			self.create_db()


	def create_db(self):
		create_db = CreateDB()
		create_db.execute()
		print('db created')


	def db_backup(self):
		print('not implemented')

