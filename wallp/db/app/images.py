
from sqlalchemy.sql.expression import func, select
from sqlalchemy.orm.exc import NoResultFound

from ..model.image import Image
from ..dbsession import DBSession


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
		self._db_session.commit()


	def random_favorite(self):
		image = self._db_session.query(Image).filter(Image.favorite == True).order_by(func.random()).first()
		image or self.raise_exc('no favorite found')
		return image


	def raise_exc(self, msg):
		raise DBImageError(msg)


		
