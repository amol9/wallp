from time import time
from os import stat

from sqlalchemy.sql.expression import func, select
from sqlalchemy.orm.exc import NoResultFound

from ..model.image import Image
from ..dbsession import DBSession
from .vars import Vars


class DBImageError(Exception):
	pass


class Images:

	def __init__(self):
		self._db_session = DBSession()


	def seen_by_url(self, url):
		count = self._db_session.query(Image).filter(Image.url == url).count()
		return count > 0


	def seen_by_context_url(self, context_url):
		count = self._db_session.query(Image).filter(Image.context_url == context_url).count()
		return count > 0


	def add(self, image):
		self._db_session.add(image)


	def commit(self):
		self._db_session.commit()


	def random_favorite(self):
		image = self._db_session.query(Image).filter(Image.favorite == True).order_by(func.random()).first()
		image or self.raise_exc('no favorite found')
		return image


	def raise_exc(self, msg):
		raise DBImageError(msg)


	def get_current_wallpaper_image(self):
		vars = Vars()
		image_id = vars.eget('current_wallpaper_image', default=None) or self.raise_exc('wallpaper image not set')
		try:
			image = self._db_session.query(Image).filter(Image.id == image_id).one()
		except NoResultFound:
			self.raise_exc('image data not available')

		return image


	def save_image(self, source, path, image):
		if image.db_image is None:
			db_image = Image()
		else:
			db_image = image.db_image

		db_image.type 	= image.type
		db_image.width 	= image.i_width
		db_image.height = image.i_height

		db_image.size = stat(path).st_size

		db_image.filepath = path
		db_image.time = int(time())

		if image.db_image is None:
			db_image.url = image.url

			db_image.title 		= image.title
			db_image.description 	= image.description[0: 1024] if image.description is not None else None
			db_image.context_url 	= image.context_url
			db_image.artist 	= image.user

			db_image.trace = source.get_trace()

			self.add(db_image)
		self.commit()	

		return db_image.id


	def update_image_score(self, image, delta):
		if image.score is not None:
			image.score += delta
		else:
			image.score = delta

		self.commit()
		return image.score


	def like_wallpaper(self):
		image = self.get_current_wallpaper_image()
		return self.update_image_score(image, 1)


	def dislike_wallpaper(self):
		image = self.get_current_wallpaper_image()
		return self.update_image_score(image, -1)


	def favorite_wallpaper(self):
		image = self.get_current_wallpaper_image()

		if image.favorite:
			self.raise_exc('image already favorited')

		image.favorite = True
		self.commit()


	def unfavorite_wallpaper(self):
		image = self.get_current_wallpaper_image()

		if not image.favorite:
			self.raise_exc('image not a favorite')

		image.favorite = False
		self.commit()


