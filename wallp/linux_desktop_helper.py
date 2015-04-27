import re
import os
import sys

from wallp.logger import log
from wallp.command import command


def get_desktop_size():
	xinfo = rc = None
	width = height = None

	with command('xdpyinfo') as c:
		xinfo, rc = c.execute()
		if rc != 0:
			log.error('xdpyinfo failed')

	dim_regex = re.compile(".*dimensions:\s+(\d+)x(\d+).*", re.M | re.S)
	m = dim_regex.match(xinfo)

	if m:
		width = int(m.group(1))
		height = int(m.group(2))

	return width, height


def set_dbus_session_vars_if_cron():
	dsba = os.environ.get('DBUS_SESSION_BUS_ADDRESS', None)
	if dsba is not None and len(dsba) > 1:
		return True

	if not os.isatty(sys.stdin.fileno()):
		log.debug('in cron session')

		uid = None
		with command('id -u') as cmd:
			uid, rc = cmd.execute()
			if rc != 0:
				log.error('could not get user id')
				return False
			uid = uid.strip()

		dbusd_pids = []
		with command('pgrep dbus-daemon -u %s'%uid) as c:
			pids, rc = c.execute()
			if rc != 0:
				log.error('could not get pid of dbus-daemon')
				return False
			dbusd_pids = pids.split()
			log.debug('dbus-daemon pids: %s'%' '.join(dbusd_pids))
						
		addr = None
		dbusd_pid = None
		for pid in dbusd_pids: 
			with command('grep -z DBUS_SESSION_BUS_ADDRESS /proc/%s/environ'%pid) as c:
				addr, rc = c.execute()
				if rc != 0:
					continue
				addr = addr.strip()
				dbusd_pid = pid	

		if addr is None:
			log.error('could not get dbus  session bus address')
			return False

		addr = addr[addr.find('=')+1:-1]
		os.environ['DBUS_SESSION_BUS_ADDRESS'] = addr
		log.debug('DBUS_SESSION_BUS_ADDRESS = %s'%addr)

		gdmsession = None
		with command('grep -z GDMSESSION /proc/%s/environ'%dbusd_pid) as cmd:
			gdmsession, rc = cmd.execute()
			if rc != 0:
				log.error('could not get GDMSESSION variable from dbus environment')
			else:
				gdmsession = gdmsession.strip()
		
		gdmsession = gdmsession[gdmsession.find('=')+1:-1]
		os.environ['GDMSESSION'] = gdmsession
		log.debug('GDMSESSION = %s'%gdmsession)

		display = None
		with command('grep -z DISPLAY /proc/%s/environ'%dbusd_pid) as cmd:
			display, rc = cmd.execute()
			if rc != 0:
				log.error('could not get DISPLAY variable from dbus environment')
			else:
				display = display.strip()
		
		display = display[display.find('=')+1:-1]
		os.environ['DISPLAY'] = display
		log.debug('DISPLAY = %s'%display)

		return True


def uses_dbus(func):
	def new_func(*args, **kwargs):
		result = set_dbus_session_vars_if_cron()
		if result:
			return func(*args, **kwargs)
		else:
			log.debug('failed to set gnome session bus address')
			return None
	return new_func

