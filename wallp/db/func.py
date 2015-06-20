from datetime import timedelta
from time import time

from .globalvars import GlobalVars
from .dbsession import DBSession
from .itemlist import ImgurAlbumList, SubredditList, SearchTermList
from .image import Image


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

	if image.score is not None:
		image.score += delta
	else:
		image.score = delta

	dbsession.commit()

	return image.score


def like_wallpaper():
	return update_wallpaper_score(1)


def dislike_wallpaper():
	return update_wallpaper_score(-1)


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


def image_url_seen(image_url):
	dbsession = DBSession()
	count = dbsession.query(Image).filter(Image.url == image_url).count()

	return count > 0
