from io import StringIO, BytesIO
import sys
from functools import partial
import socket

from mutils.system import *

from ..globals import Const
from .webcache import WebCache
from ..service.service import ServiceError
from ..util.logger import log
from .exc import DownloadError, TimeoutError

if is_py3():
	from urllib.error import HTTPError
	from urllib.request import urlopen
else:
	from urllib2 import HTTPError, urlopen, URLError


cache = None
if Const.cache_enabled:
	cache = WebCache()


def exists(url):
	try:
		res = urlopen(url, timeout=10)
		if res.code == 200:
			res.close()
			return True
	except (URLError, HTTPError) as e:
		return False


def get_page(url, progress=True, nocache=False):
	return download(url, progress=progress, nocache=nocache)


def download(url, save_filepath=None, progress=True, nocache=False, open_file=None):
	'''if eh:
		dcm = DownloadCM()
		dcm._meth = partial(download, url, save_filepath=save_filepath, progress=progress, nocache=nocache)
		return dcm'''

	if not nocache and Const.cache_enabled:
		data = cache.get(url)
		if data is not None:
			print_progress_ast()
			#if log.to_stdout(): print('')
			if save_filepath is None:
				if is_py3():
					data = data.decode(encoding='utf-8')	
				return data
			else:
				with open(save_filepath, 'wb') as f:
					f.write(data)
				return
	
	chunksize = 40000
	res = None
	try:
		res = urlopen(url)

	except HTTPError as e:
		log.error(str(e) + ' ' + url)
		raise DownloadError()

	except URLError as e:
		if type(e.reason) == socket.timeout:
			log.error(str(e) + ' ' + url)
			raise TimeoutError()
		raise DownloadError()

	out = None
	if save_filepath == None:
		if open_file == None:
			out = BytesIO()
		else:
			out = open_file
	else:
		out = open(save_filepath, 'wb+')

	chunk = res.read(chunksize)
	while chunk:
		if progress: print_progress_dot()
		buf = bytes(chunk)
		out.write(buf)
		chunk = res.read(chunksize)

	#if log.to_stdout(): print('')
	res.close()

	if not nocache and Const.cache_enabled:
		out.seek(0)
		cache.add(url, out.read())

	if save_filepath is None and open_file is None:
		out.seek(0)
		buf = out.read()
		out.close()
		if is_py3():
			buf = buf.decode(encoding='utf-8')
		return buf
	elif save_filepath is not None:
		out.close()
		return True



def print_progress_dot():
	prints('.')


def print_progress_ast():
	prints('*')
