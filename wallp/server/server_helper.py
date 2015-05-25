from datetime import timedelta
from time import time
import os

from .wallpaper_image import WallpaperImage
from .protocol.wp_change_message import WPState
from ..command import command


class StartError(Exception):
	pass


class ServerStats():
	def __init__(self):
		self.peak_clients = 0
		self.start_time = None
		self.current_clients = 0
		self.peak_fds = 0
		self.open_fds = 0
		self.avg_client_lifetime = None


	def update_clients(self, count):
		if self.peak_clients < count:
			self.peak_clients = count
		self.current_clients = count


	def update_open_fds(self):
		open_fds = None
		with command('ls /proc/%d/fd | wc -l'%os.getpid()) as cmd:
			out, r = cmd.execute()
			if r == 0:
				open_fds = int(out)
			else:
				log.error('unable to obtain open fd count')
				return

		if open_fds > self.peak_fds:
			self.peak_fds = open_fds
		self.open_fds = open_fds


	def update_client_lifetime(self, lifetime):
		if self.avg_client_lifetime is None:
			self.avg_client_lifetime = lifetime
		else:
			self.avg_client_lifetime = (self.avg_client_lifetime + lifetime) / 2


	def __repr__(self):
		repr = ''
		repr += 'peak clients: %d\n'%self.peak_clients
		repr += 'live clients: %d\n'%self.current_clients
		repr += 'peak fds: %d\n'%self.peak_fds
		repr += 'open fds: %d\n'%self.open_fds
		repr += 'avg client life: '
		if self.avg_client_lifetime is None:
			repr += 'n.a.\n'
		else:
			repr += '%.2fs\n'%self.avg_client_lifetime
		repr += 'uptime: %s\n'%(str(timedelta(seconds=(int(time() - self.start_time)))))

		return repr


class GenericLimits():
	max_message_size = 10 * 1024 * 1024
	max_messages_in_queue_per_conn = 10
	max_line_message_length = 512


class LinuxLimits(GenericLimits):
	select = 1024
	clients = 1014


def get_limits():
	return LinuxLimits()


class ServerSharedState():
	def __init__(self):
		self.in_pipes = []
		self.out_pipes = []

		self.client_list = []
		self.telnet_client_list = []
		self.last_change = None
		self.wp_image = WallpaperImage()
		self.wp_state = WPState.NONE


	def abort_image_producers(self):
		for transport in self.client_list:
			transport.unregisterProducer()


