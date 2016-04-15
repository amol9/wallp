from datetime import datetime

from redlib.api.http import HttpRequest, GlobalOptions, RequestOptions, HttpError
from redlib.api.prnt import format_size

from .. import const
from ..util.logger import log
from ..util.printer import printer
from ..db.app.config import Config, ConfigError


http_global_options = None
try:
	http_global_options = GlobalOptions(cache_dir=const.cache_dir, chunksize=const.http_chunksize,
			timeout=Config().eget('http.timeout', const.http_timeout))
except ConfigError as e:
	log.error(e)

httprequest = HttpRequest(global_options=http_global_options)


def get(url, save_filepath=None, open_file=None, callbacks=None, msg=None, headers=None, max_content_length=None, save_to_temp_file=False):
	roptions = RequestOptions(save_filepath=save_filepath, open_file=open_file, headers=headers,
			save_to_temp_file=save_to_temp_file, max_content_length=max_content_length)

	if msg is not None:
		cb = printer.printf(msg, '?', progress=True)
		callbacks = cb

	if callbacks is not None:
		roptions.progress_cb 		= callbacks.progress_cb
		roptions.progress_cp 		= callbacks.progress_cp
		roptions.content_length_cb	= lambda c : cb.col_updt_cb(0, format_size(c))
		roptions.rate_cb		= lambda c : cb.col_updt_cb(2, format_size(c) + '/s')
		roptions.cached_cb		= lambda i : cb.col_updt_cb(2, '[cached %s]'%(timestamp_to_date_str(i.get('mtime', None))))

	return httprequest.get(url, roptions)


def timestamp_to_date_str(ts):
	if ts is not None:
		return datetime.fromtimestamp(ts).strftime('%d-%b-%Y %H:%M:%S')
	else:
		return ''


def exists(url):
	return httprequest.exists(url)

