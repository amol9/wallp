from time import sleep

from ..client.helper import get_image, compute_style
from ..desktop.desktop_factory import get_desktop, DesktopException
from .protocol.wp_change_message import WPState
from ..util.logger import log


class ChangeWallpaper():
	def __init__(self, transport):
		self._transport = transport


	def execute(self):
		log.debug('changing wallpaper..')
		try:
			self.send_to_server(WPState.CHANGING)
			sleep(6)

			#wp_path = get_image(service_name='bitmap', query=None, color=None)
			#print 'wp_path:', wp_path

			#style = compute_style(wp_path)

			#dt = get_desktop()
			#dt.set_wallpaper(wp_path, style=style)

			self.send_to_server(WPState.READY)
			self.send_to_server('/home/amol/Pictures/wallp.jpg')
			#self.send_to_server(wp_path)
		
		except DesktopException:
			#log.error('cannot change wallpaper')
			self.send_to_server(WPState.ERROR)

		except ServiceError as e:
			log.error(str(e))
		

	def send_to_server(self, message):
		self._transport.write_blocking(message)

