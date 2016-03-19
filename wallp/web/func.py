
from redlib.api.http import HttpRequest, GlobalOptions, RequestOptions, HttpError
from redlib.api.prnt import format_size

from ..globals import Const
from ..util.printer import printer


http_global_options = GlobalOptions(cache_dir=Const.cache_dir, chunksize=Const.http_chunksize, timeout=30)
httprequest = HttpRequest(global_options=http_global_options)

def get(url, save_filepath=None, open_file=None, callbacks=None, msg=None, headers=None, max_content_length=None):
	roptions = RequestOptions(save_filepath=save_filepath, open_file=open_file, headers=headers, max_content_length=max_content_length)

	if msg is not None:
		cb = printer.printf(msg, '?', progress=True, col_cb=True)
		clc = lambda c : cb.col_cb(2, format_size(c))
		cb.content_length_cb = clc
		callbacks = cb

	if callbacks is not None:
		roptions.progress_cb 		= callbacks.progress_cb
		roptions.progress_cp 		= callbacks.progress_cp
		roptions.content_length_cb	= callbacks.content_length_cb


	return httprequest.get(url, roptions)


def exists(url):
	return httprequest.exists(url)

