from io import StringIO, BytesIO
import sys
from functools import partial
import socket
import requests

from redlib.api.system import *
from redlib.api.prnt import prints, format_size

from ..globals import Const
from .webcache import WebCache
from ..service.service import ServiceError
from ..util.logger import log
from .exc import DownloadError, TimeoutError
from ..util.printer import printer


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


def get_page(url, progress=True, nocache=False, headers=None, msg='', print_size=False):
	if progress:
		cb = printer.printf(msg, '?', progress=True, col_cb=True)
		clc = lambda c : cb['col_cb'](2, format_size(c))
		return download(url, progress_cb=cb['progress_cb'], progress_cp=cb['progress_cp'], nocache=nocache, headers=headers,
				content_length_cb=clc)
	else:
		return download(url, progress=progress, nocache=nocache, headers=headers)


def exc_wrapped_call(func, *args, **kwargs):
	progress_cp = kwargs.pop('progress_cp', None)
	
	try:
		r = func(*args, **kwargs)
		return r

	except (URLError, HTTPError, requests.exceptions.HTTPError) as e:
		log.error(e)
		if progress_cp is not None:
			progress_cp()
		printer.printf('error', str(e))

		if type(e.reason) == socket.timeout:
			raise TimeoutError()
		else:
			raise DownloadError()


def exc_wrapped(func):
	def new_func(*args, **kwargs):
		return exc_wrapped_call(func, *args, **kwargs)
	return new_func


def download(url, save_filepath=None, progress=False, nocache=False, open_file=None, headers=None, progress_cb=None,
		progress_cp=None, content_length_cb=None):

	if not nocache and Const.cache_enabled:
		data = WebCache().get(url)
		if data is not None:
			#print_progress_ast()
			if content_length_cb is not None:
				content_length_cb(len(data))

			if progress_cb is not None:
				progress_cp('[cached]')

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
		res = exc_wrapped_call(urlopen, url, timeout=Const.page_timeout, progress_cp=progress_cp)
	else:
		res = exc_wrapped_call(urlopen, Request(url, None, headers), timeout=Const.page_timeout, progress_cp=progress_cp)

	out = None
	if save_filepath == None:
		if open_file == None:
			out = BytesIO()
		else:
			out = open_file
	else:
		out = open(save_filepath, 'wb+')

	content_length = res.headers.getheader('Content-Length')
	if content_length is not None:
		content_length = int(content_length) 

		if content_length_cb is not None:
			content_length_cb(content_length)

	content_done = 0
	chunk = res.read(chunksize)
	while chunk:
		if progress: 
			print_progress_dot()
		buf = bytes(chunk)
		out.write(buf)

		content_done += len(chunk)
		if progress_cb is not None:
			if content_length is not None:
				progress_cb((float(content_done) / content_length) * 100)
			else:
				progress_cb(-1)

		chunk = res.read(chunksize)

	if content_length is None and content_length_cb is not None:
		content_length_cb(content_done)

	if progress_cp is not None:
		progress_cp()

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
	prints('. ')


def print_progress_ast():
	prints('* ')

