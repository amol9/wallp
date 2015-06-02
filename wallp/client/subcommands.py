
from ..db import Config
from ..util import Scheduler
from . import change_wallpaper
from ..util import log


class Subcommands:
	def __init__(self):
		self._args = None


	def change(self):
		assert self._args

		spec = CWSpec()
		spec.service_name = self._args.service
		spec.query = self._args.query
		spec.color = self._args.color

		change_wallpaper(spec)


	def schedule(self):
		assert self._args

		scheduler = Scheduler()
		scheduler.set_frequency(self._args.frequency)


	def log(self):
		assert self._args

		log.start(self._args.filename, self._args.level)


	def set(self):
		assert self._args

		config = Config()
		config.set(self._args.name, self._args.value)


	def get(self):
		assert self._args

		config = Config()
		value = config.get(self._args.name)
		print(value)


	def add(self):
		assert self._args

		list = get_list()	#temp
		list.add(self._args.item)


