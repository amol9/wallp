from io import StringIO, BytesIO
import sys
from functools import partial

from mutils.system import *

from ..globals import Const
from .webcache import WebCache
from ..service.service import ServiceException
from ..util.logger import log

if is_py3():
	from urllib.error import HTTPError
	from urllib.request import urlopen
else:
	from urllib2 import HTTPError, urlopen


cache = None
if Const.cache_enabled:
	cache = WebCache()


class DownloadCM():
	def __enter__(self):
		return self


	def start(self):
		if self._meth is not None:
			return self._meth()


	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type == HTTPError:
			raise ServiceException()


def download(url, save_filepath=None, progress=True, nocache=False):
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
		raise e

	out = None
	if save_filepath == None:
		out = BytesIO()
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

	if save_filepath == None:
		out.seek(0)
		buf = out.read()
		out.close()
		if is_py3():
			buf = buf.decode(encoding='utf-8')
		return buf
	else:
		out.close()
		return True


def print_progress_dot():
	prints('.')


def print_progress_ast():
	prints('*')
