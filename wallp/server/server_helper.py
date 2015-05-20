
class ServerStats():
	def __init__(self):
		self.peak_clients = 0
		self.start_time = None
		self.current_clients = 0


	def update_clients(self, count):
		if self.peak_clients < count:
			self.peak_clients = count
		self.current_clients = count


	def __repr__(self):
		repr = ''
		repr += 'peak clients: %d\n'%self.peak_clients
		repr += 'live clients: %d\n'%self.current_clients
		repr += 'uptime: %s'%(str(timedelta(seconds=(int(time() - self.start_time)))))

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
		self.in_list = []

		self.client_list = []
		self.last_change = None
		self.wp_image = WallpaperImage()
		self.wp_state = WPState.NONE


	def abort_image_producers(self):
		for transport in self.client_list:
			transport.unregisterProducer()


