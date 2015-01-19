from io import StringIO, BytesIO
import urllib2
from urllib2 import HTTPError
import sys

from wallp.globals import Const
from wallp.webcache import WebCache


cache = None
if Const.cache_enabled:
	cache = WebCache()


def download(url):
	pass	


def download(url, save_filepath=None, progress=True, nocache=False):
	if not nocache and Const.cache_enabled:
		data = cache.get(url)
		if data is not None:
			print_progress_ast()
			print('')
			return data
	
	chunksize = 40000
	res = None
	try:
		res = urllib2.urlopen(url)
	except HTTPError as e:
		raise e

	out = None
	if save_filepath == None:
		out = BytesIO()
	else:
		out = open(save_filepath, 'w+')

	chunk = res.read(chunksize)
	while chunk:
		if progress: print_progress_dot()
		buf = bytes(chunk)
		out.write(buf)
		chunk = res.read(chunksize)

	print('')
	res.close()

	if not nocache and Const.cache_enabled:
		out.seek(0)
		cache.add(url, out.read())

	if save_filepath == None:
		out.seek(0)
		buf = out.read()
		out.close()
		return buf
	else:
		out.close()
		return True


def print_progress_dot():
	print('.'),; sys.stdout.flush()


def print_progress_ast():
	print('*'),; sys.stdout.flush()
