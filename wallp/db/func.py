from datetime import timedelta
from time import time

from .globalvars import GlobalVars
from .dbsession import DBSession
from .itemlist import ImgurAlbumList, SubredditList, SearchTermList


def update_wallpaper_score(delta):
	globalvars = GlobalVars()
	image_id = globalvars.get('current_wallpaper_image')

	if image_id is None:
		raise LikeError('no wallpaper set')

	dbsession = DBSession()
	result = dbsession.query(Image).filter(Image.id == image_id).all()

	if len(result) == 0:
		raise LikeError('wallpaper image not found')

	image = result[0]

	image.score += delta
	image.save()

	return image.score


def like_wallpaper():
	update_wallpaper_score(1)


def dislike_wallpaper():
	update_wallpaper_score(-1)


def keep_wallpaper(period):
	period_map = { 's': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks' }
	period_regex = re.compile("(\d{1,3})((m|h|d|w|M|Y))")

	match = period_regex.match(period)
	
	if match is None:
		raise KeepError('bad time period')

	num = int(match.group(1))
	abbr_period = match.group(2)
	tdarg = {}	

	if abbr_period == 'M':
		tdarg['days'] = 30 * num
	elif abbr_period == 'Y':
		tdarg['days'] = 365 * num
	else:
		tdarg[period_map[abbr_period]] = num

	td = timedelta(**tdarg)
	keep_timeout = int(time()) + td.total_seconds()

	globalvars = GlobalVars()
	globalvars.set('keep_timeout', keep_timeout)


def get_last_change_time():
	globalvars = GlobalVars()
	return globalvars.get('last_change_time')


def set_last_change_time():
	globalvars = GlobalVars()
	globalvars.set('last_change_time', int(time()))


def get_lists():
	return [ImgurAlbumList, SubredditList, SearchTermList]

