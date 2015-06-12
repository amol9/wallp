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


def get_last_change_time():
	globalvars = GlobalVars()
	return globalvars.get('last_change_time')


def get_lists():
	return [ImgurAlbumList, SubredditList, SearchTermList]


def get_current_wallpaper_image():
	image_id = GlobalVars().get('current_wallpaper_image')
	result = DBSession().query(Image).filter(Image.id == image_id).all()

	if len(result) == 0:
		raise NotFoundError()

	return result[0]

