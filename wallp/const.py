from os.path import join as joinpath, expanduser
from os import environ

from redlib.api.system import *


app_name 		= 'wallp'
app_description		= 'A command line utility to download and set wallpapers from various sources.'
debug 			= False
wallpaper_basename 	= 'wallp' + ('_debug' if debug else '')
data_dir 		= environ.get('WALLP_DATA_DIR', None) or expanduser('~/.wallp')
cache_dir 		= expanduser(joinpath(data_dir, 'cache'))
cache_enabled 		= True
image_extensions 	= ['jpg', 'png', 'bmp', 'jpeg']
script_name 		= 'wallp'
scheduler_task_name 	= 'wallp_scheduled_task'
scheduler_cmdname	= 'wallps' if is_windows() else script_name
scheduler_cmdline	= '%s source random'%scheduler_cmdname	
db_name 		= 'wallp.db'
db_path 		= joinpath(data_dir, db_name)
http_timeout		= 15
default_server_port	= 40002
http_chunksize		= 50 * 1024
max_image_size		= 4 * 1024 * 1024
min_ratio_to_desktop	= 0.8
max_ratio_to_desktop	= 3.0
ignore_image_filter	= False

logfile			= joinpath(data_dir, 'wallp.log')
db_logfile		= joinpath(data_dir, 'db.log')


