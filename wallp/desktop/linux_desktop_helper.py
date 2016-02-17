import re
import os
import sys


from redlib.api.system import sys_command, is_windows

from ..util.logger import log


'''def is_cron_session():
	return not os.isatty(sys.stdin.fileno())


def are_dbus_session_vars_set():
	dsba = os.environ.get('DBUS_SESSION_BUS_ADDRESS', None)
	if dsba is not None and len(dsba) > 1:
		return True


def set_dbus_session_vars_if_cron():
	if are_dbus_session_vars_set():
		return True

	if is_cron_session():
		log.debug('in cron session')

		uid = os.getuid()
		if uid == None: 
			log.error('could not get user id')
			return False

		dbusd_pids = []
		rc, pids = sys_command('pgrep dbus-daemon -u %s'%uid)
		if rc != 0:
			log.error('could not get pid of dbus-daemon')
			return False
		dbusd_pids = pids.split()
		log.debug('dbus-daemon pids: %s'%' '.join(dbusd_pids))

		dbus_session_bus_addr = None
		dbus_session_bus_addr_re = re.compile(b'DBUS_SESSION_BUS_ADDRESS.*?\x00')

		for pid in dbusd_pids:
			dbusd_environ = None
			with open('/proc/%s/environ'%pid, 'rb') as f:
				dbusd_environ = f.read()

			matches = dbus_session_bus_addr_re.findall(dbusd_environ)
			if len(matches) == 0:
				continue

			dbus_session_bus_addr = matches[0][matches[0].index('=') + 1:-1]

			log.debug('DBUS_SESSION_BUS_ADDRESS = %s'%dbus_session_bus_addr)
			os.environ['DBUS_SESSION_BUS_ADDRESS'] = dbus_session_bus_addr
			log.testresult(dbus_session_bus_addr)

			matches = re.compile(b'GDMSESSION.*?\x00').findall(dbusd_environ)

			if len(matches) == 0:
				log.error('GDMSESSION not found in dbus-daemon environment')
			else:
				gdmsession = matches[0][matches[0].index('=') + 1:-1]
				log.debug('GDMSESSION = %s'%gdmsession)
				os.environ['GDMSESSION'] = gdmsession
				log.testresult(gdmsession)

			matches = re.compile(b'DISPLAY.*?\x00').findall(dbusd_environ)

			if len(matches) == 0:
				log.error('DISPLAY not found in dbus-daemon environment')
			else:
				display = matches[0][matches[0].index('=') + 1:-1]
				log.debug('DISPLAY = %s'%display)
				os.environ['DISPLAY'] = display
				log.testresult(display)

			return True

		return False


def uses_dbus(func):
	if is_windows():
		return func

	def new_func(*args, **kwargs):
		result = set_dbus_session_vars_if_cron()
		if result:
			return func(*args, **kwargs)
		else:
			log.debug('failed to set gnome session bus address')
			return None
	return new_func'''


def get_desktop_size():
	xinfo = rc = None
	width = height = None

	rc, xinfo = sys_command('xdpyinfo')
	if rc != 0:
		log.error('xdpyinfo failed')

	dim_regex = re.compile(".*dimensions:\s+(\d+)x(\d+).*", re.M | re.S)
	m = dim_regex.match(xinfo)

	if m:
		width = int(m.group(1))
		height = int(m.group(2))

	return width, height


