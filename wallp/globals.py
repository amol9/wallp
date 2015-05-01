from os.path import join as joinpath, expanduser

from mutils.system import *


class Const():
	app_name = 'wallpaper_app'
	config_filename = 'wallp.config'
	debug = False
	wallpaper_basename = 'wallp' + ('_debug' if debug else '')
	data_dir = expanduser('~/.wallp')
	cache_dir = expanduser(joinpath(data_dir, 'cache'))
	config_filepath = expanduser(joinpath(data_dir, config_filename))
	cache_enabled = True
	image_extensions = ['jpg', 'png', 'bmp', 'jpeg']
	script_name = 'wallp'
	scheduler_task_name = 'wallp_scheduled_task'
	scheduler_cmd = 'wallps' if is_windows() else script_name 
