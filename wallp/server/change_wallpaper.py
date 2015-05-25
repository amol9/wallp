from time import sleep

from ..helper import get_image, compute_style
from ..desktop_factory import get_desktop, DesktopException
from .protocol.wp_change_message import WPState


class ChangeWallpaper():
	def __init__(self, transport):
		self._transport = transport


	def execute(self):
		print 'changing wallpaper..'
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
		except Exception as e:
			print e.message
		

	def send_to_server(self, message):
		self._transport.write_blocking(message)

