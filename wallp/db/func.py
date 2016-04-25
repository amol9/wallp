from datetime import timedelta
from time import time
from random import choice

from .app.vars import Vars
from .dbsession import DBSession
from .model.image import Image
from .exc import NotFoundError


class FavoriteError(Exception):
	pass


def get_wallpaper_image():
	vars = Vars()
	image_id = vars.eget('current_wallpaper_image', default=None)

	if image_id is None:
		raise LikeError('no wallpaper set')

	result = DBSession().query(Image).filter(Image.id == image_id).all()

	if len(result) == 0:
		raise LikeError('wallpaper image not found')

	image = result[0]
	return image


def update_image_score(image, delta):
	if image.score is not None:
		image.score += delta
	else:
		image.score = delta

	DBSession().commit()

	return image.score


def like_wallpaper():
	image = get_wallpaper_image()
	return update_image_score(image, 1)


def dislike_wallpaper():
	image = get_wallpaper_image()
	return update_image_score(image, -1)


def favorite_wallpaper():
	image = get_wallpaper_image()

	if image.favorite:
		raise FavoriteError('image already favorited')

	image.favorite = True
	DBSession().commit()


def get_random_favorite():
	result = DBSession().query(Image).filter(Image.favorite==True).all()

	if len(result) == 0:
		raise FavoriteError('no favorites found')

	return choice(result)


def unfavorite_wallpaper():
	image = get_wallpaper_image()

	if not image.favorite:
		raise FavoriteError('image not a favorite')

	image.favorite = False
	DBSession().commit()


def get_last_change_time():
	vars = Vars()
	return vars.eget('last_change_time', default=None)


def get_current_wallpaper_image():
	vars = Vars()
	image_id = vars.eget('current_wallpaper_image', default=None)
	result = DBSession().query(Image).filter(Image.id == image_id).all()

	if len(result) == 0:
		raise NotFoundError()

	return result[0]


def image_url_seen(image_url):
	count = DBSession().query(Image).filter(Image.url == image_url).count()

	return count > 0
