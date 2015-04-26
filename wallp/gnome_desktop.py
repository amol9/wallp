
from wallp.desktop import Desktop
from wallp.logger import log
from wallp.command import command
from wallp.config import config
import wallp.linux_desktop_helper as ldh


class GnomeDesktop(Desktop):
	wp_styles = {
		'none': 'none',
		'tiled': 'wallpaper',
		'centered': 'centered',
		'scaled': 'scaled',
		'stretched': 'strecthed',
		'zoom': 'zoom'
	}


	def cron(func):
		def new_func(*args):
			result = LinuxDesktop.setup_dbus_addr_if_cron(args[0])
			if result:
				return func(*args)
			else:
				log.debug('failed to set gnome session bus address')
				return None
		return new_func


	@cron
	def get_size(self):
		return ldh.get_desktop_size()

	
	@cron
	def set_wallpaper(self, filepath, style=None):
		cmd = 'gsettings set org.gnome.desktop.background picture-uri file://%s'%filepath
		with command(cmd) as c:
			c.execute()
		
		if style is not None:
			self.set_wallpaper_style(style)


	@cron
	def set_wallpaper_style(self, style):
		wp_style = self.wp_styles.get(style)
		if wp_style is None:
			wp_style = self.wp_styles['none']

		cmd = 'gsettings set org.gnome.desktop.background picture-options %s'%wp_style
		with command(cmd) as c:
			c.execute()


	def setup_dbus_addr_if_cron(self):
		if not os.isatty(sys.stdin.fileno()):
			log.debug('in cron session')

			gs_pid = None
			with command('pgrep gnome-session') as c:
				gs_pid, rc = c.execute()
				if rc != 0:
					log.debug('could not get pid of gnome-session')
					return False
				gs_pid = gs_pid.strip()
				
				
			addr = None 
			with command('grep -z DBUS_SESSION_BUS_ADDRESS /proc/%s/environ'%gs_pid) as c:
				addr, rc = c.execute()
				if rc != 0:
					log.debug('could not get gnome session bus address')
					return False
				addr = addr.strip()

			os.environ['DBUS_SESSION_BUS_ADDRESS'] = addr[addr.find('=')+1:-1]
		else:
			pass
		return True


