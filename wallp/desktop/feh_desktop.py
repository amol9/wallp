from os.path import exists, expanduser, join as joinpath
import re

from redlib.api.system import sys_command, CronDBus, CronDBusError
from redlib.api.misc import TextFile, TextFileError

from .desktop import Desktop, DesktopError
from .wpstyle import WPStyle
from ..util.logger import log
from ..util.printer import printer
from .linux_desktop_helper import get_desktop_size


# for any desktop supported by feh
class FehDesktop(Desktop):
	wp_styles = {
		WPStyle.NONE : 		'--bg-center',
		WPStyle.TILED : 	'--bg-tile',
		WPStyle.CENTERED : 	'--bg-center',
		WPStyle.SCALED : 	'--bg-max',
		WPStyle.STRETCHED : 	'--bg-scale',
		WPStyle.ZOOM : 		'--bg-fill'
	}

	@staticmethod
	def supports(gdmsession, xdg_current_desktop):
		if xdg_current_desktop is not None and xdg_current_desktop == 'i3':
			rc, _ = sys_command('which feh')
			if rc == 0:
				return True
			else:
				raise DesktopError('feh is not installed; sudo apt-get install feh?')
	

	def __init__(self):
		pass


	def get_size(self):
		return get_desktop_size()

	
	def set_wallpaper(self, filepath, style=None):
		bg_style = self.wp_styles.get(int(style if style is not None else WPStyle.NONE))
		cmd = 'feh %s %s'%(bg_style, filepath)
		sys_command(cmd)

		self.persist()
		

	def set_wallpaper_style(self, style):
		bg_style = self.wp_styles.get(int(style if style is not None else WPStyle.NONE))
		_, filepath = self.load_fehbg()
		cmd = 'feh %s %s'%(bg_style, filepath)
		sys_command(cmd)


	def get_wallpaper(self):
		_, filepath = self.load_fehbg()
		return filepath
	
	
	def get_wallpaper_style(self):
		style_flag, _ = self.load_fehbg()
		style = dict([(v, k) for (k, v) in self.wp_styles.items()]).get(style_flag, None)

		return WPStyle(style)
		

	def load_fehbg(self):
		path = expanduser('~/.fehbg')
		if not exists(path):
			raise DesktopError('file: %s not found'%path)

		fehbg = None
		with open(path, 'r') as f:
			fehbg = f.read()

		re_fehcmd = re.compile(".*feh\s+.*(--bg-center|--bg-tile|--bg-scale|--bg-max|--bg-fill)\s+'(.*)'", re.M | re.S)
		m = re_fehcmd.match(fehbg)

		if m is not None:
			style_flag = m.group(1)
			filepath = m.group(2)
		else:
			raise DesktopError('file: ~/.fehbg cannot be parsed')

		return style_flag, filepath


	def persist(self):
		config_dir = expanduser('~/.config/i3')

		if not exists(config_dir):
			printer.printf('warning', 'dir: %s not found, wallpaper will not persist after logout'%config_dir)
			return

		config_file = joinpath(config_dir, 'config')
		tfile = TextFile(config_file)

		if not tfile.find_section('wallp_fehbg_persist'):
			tfile.append_section('exec ~/.fehbg', id='wallp_fehbg_persist')
			printer.printf('note', 'config file: %s modified to make wallpaper persistent'%config_file)

