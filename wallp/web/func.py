from io import StringIO, BytesIO
import sys
from functools import partial
import socket
import requests

from mutils.system import *

from ..globals import Const
from .webcache import WebCache
from ..service.service import ServiceError
from ..util.logger import log
from .exc import DownloadError, TimeoutError

if is_py3():
	from urllib.error import HTTPError, URLError
	from urllib.request import urlopen, Request
else:
	from urllib2 import HTTPError, urlopen, URLError, Request


def exists(url):
	try:
		res = urlopen(url, timeout=10)
		if res.code == 200:
			res.close()
			return True
	except (URLError, HTTPError) as e:
		return False


def get_page(url, progress=True, nocache=False, headers=None):
	return download(url, progress=progress, nocache=nocache, headers=headers)


def exc_wrapped_call(func, *args, **kwargs):
	try:
		r = func(*args, **kwargs)
		return r

	except (HTTPError, requests.exceptions.HTTPError) as e:
		log.error(str(e))
		raise DownloadError()

	except URLError as e:
		if type(e.reason) == socket.timeout:
			log.error(str(e))
			raise TimeoutError()
		raise DownloadError()


def exc_wrapped(func):
	def new_func(*args, **kwargs):
		return exc_wrapped_call(func, *args, **kwargs)
	return new_func


def download(url, save_filepath=None, progress=True, nocache=False, open_file=None, headers=None):
	if not nocache and Const.cache_enabled:
		data = WebCache().get(url)
		if data is not None:
			print_progress_ast()

			if save_filepath is None:
				if is_py3():
					data = data.decode(encoding='utf-8')	
				return data
			else:
				with open(save_filepath, 'wb') as f:
					f.write(data)
				return
	
	chunksize = Const.http_chunksize
	res = None

	if headers is None:
		res = exc_wrapped_call(urlopen, url, timeout=Const.page_timeout)
	else:
		res = exc_wrapped_call(urlopen, Request(url, None, headers), timeout=Const.page_timeout)

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

	res.close()

	if not nocache and Const.cache_enabled:
		out.seek(0)
		WebCache().add(url, out.read())

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

