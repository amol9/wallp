
from ..model.image import Image
from ..dbsession import DBSession


class Images:

	def seen_by_url(self, url):
		count = DBSession().query(Image).filter(Image.url == url).count()
		return count > 0


	def seen_by_context_url(self, context_url):
		count = DBSession().query(Image).filter(Image.context_url == context_url).count()
		return count > 0


	def add(self, image):
		DBSession().add(image)
		DBSession().commit()

