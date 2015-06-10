
from mutils.system import Scheduler

from ..db import Config, func
from ..util import log


class Subcommands:
	def __init__(self):
		self._args = None


	def change(self):
		args = self._args
		client = Client(service_name=args.service_name, query=args.query, color=args.color)
		client.change_wallpaper()


	def schedule(self):
		scheduler = Scheduler()
		scheduler.set_frequency(self._args.frequency)


	def log(self):
		log.start(self._args.filename, self._args.level)


	def set(self):
		config = Config()
		config.set(self._args.name, self._args.value)


	def set_server(self):
		config = Config()
		config.set('server.host', self._args.host)
		config.set('server.port', self._args.port)


	def get(self):
		config = Config()
		value = config.get(self._args.name)
		print(value)


	def get_item_list(self):
		item_list = [l for l in func.get_lists() if l.name == self._args.list_name]
		if len(item_list) == 0:
			raise AppError('%s is not a valid list'%self._args.list_name)
		elif len(item_list) > 1:
			raise AppErrpr('too many lists named %s, something is very wrong'%self._args.list_name)


	def itemlist_call(self, func, *args):
		try:
			func(*args)
		except (ValueError, NotFoundError) as e:
			raise AppError(str(e))


	def add(self):
		item_list = self.get_item_list()
		self.itemlist_call(item_list.add, self._args.item)


	def enable(self):
		item_list = self.get_item_list()
		self.itemlist_call(item_list.enable, self._args.item)


	def disable(self):
		item_list = self.get_item_list()
		self.itemlist_call(item_list.disable, self._args.item)


	def like(self):
		func.like_wallpaper()
		

	def dislike(self):
		func.dislike_wallpaper()


	def keep(self):
		func.keep_wallpaper(self._args.period)
