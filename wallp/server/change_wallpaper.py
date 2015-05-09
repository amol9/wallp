
from ..helper import get_image, compute_style
from ..desktop_factory import get_desktop, DesktopException


class WPState():
	NONE = 0
	READY = 1
	CHANGING = 2


class ChangeWallpaper():
	def __init__(self, outpipe):
		self._outpipe = outpipe


	def execute(self):
		print 'changing wallpaper..'
		try:
			self.send_to_server(WPState.CHANGING)

			wp_path = get_image(service_name='bitmap', query=None, color=None)
			print 'wp_path:', wp_path

			style = compute_style(wp_path)

			dt = get_desktop()
			dt.set_wallpaper(wp_path, style=style)

			self.send_to_server(WPState.READY)
		
		except DesktopException:
			#log.error('cannot change wallpaper')
			pass
		

	def send_to_server(self, wp_state):
		self._outpipe.send(wp_state)

