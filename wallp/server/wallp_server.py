import socket
import os
from os.path import exists
from time import time
import logging

from mayloop.server import Server
from mayloop.config import Config

from .scheduler import Scheduler
from .change_wallpaper import ChangeWallpaper
from .wallpaper_image import WallpaperImage
from .protocol.wallp_server import WallpServer
from .protocol.wp_change_message import WPChangeMessage, WPState
from .factory.wallp_server_factory import WallpServerFactory
from .factory.wp_change_message_factory import WPChangeMessageFactory
from ..util.logger import log


def scheduled_task_placeholder():
	pass


class WallpServer():
	def __init__(self, port):
		self._port = port
		self._server = None
		self._wp_state = WPState()
		self._wp_image = WallpaperImage()
		self._change_wp = None


	def start_scheduler(self):
		self._scheduler = Scheduler()

		self.setup_job()
		self._scheduler.start()


	def start_protocol_factories(self):
		self._wallp_server_factory = WallpServerFactory(self._wp_state, self._wp_image)
		self._wp_change_message_factory = WPChangeMessageFactory(self._wp_state, self._wp_image)


	def setup_job(self):
		global scheduled_task_placeholder
		self._scheduler.add_job(scheduled_task_placeholder, '5s', 'change_wallpaper')
		scheduled_task_placeholder = self._change_wp.execute


	def start(self):
		self.start_protocol_factories()

		config = Config()
		config.add_service('', self._port, self._wallp_server_factory)
		pipe = config.add_pipe(self._wp_change_message_factory)

		config.set_logger(log) 
		config.start_logger(level=logging.DEBUG)

		config.do_after_start(self.after_start, pipe)

		self._server = Server(config)
		self._server.start()


	def after_start(self, pipe):
		self._change_wp = ChangeWallpaper(pipe.transport)
		self.start_scheduler()


	'''def stop(self):
		self._scheduler.shutdown()
		self._pause_server = True

		for c in self.client_list:
			self.transport_call(c.abortConnection)
		self._server.close()
		self._server = None


	def hot_start(self):
		self.start_server_socket()
		self._pause_server = False
		self._scheduler.start()


	def pause(self):
		self._scheduler.pause()
		self._pause_server = True


	def resume(self):
		self._scheduler.start()
		self.start_select_loop()'''

