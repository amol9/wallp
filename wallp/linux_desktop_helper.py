import re

from wallp.logger import log
from wallp.command import command

def get_desktop_size():
	xinfo = rc = None
	width = height = None

	with command('xdpyinfo') as c:
		xinfo, rc = c.execute()

	dim_regex = re.compile(".*dimensions:\s+(\d+)x(\d+).*", re.M | re.S)
	m = dim_regex.match(xinfo)

	if m:
		width = int(m.group(1))
		height = int(m.group(2))

	return width, height

