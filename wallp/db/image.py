from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from . import Base, DBSession
from .image_trace import ImageTrace


class Image(Base):
	__tablename__ = 'image'

	id = 		Column(Integer, primary_key=True)
	type = 		Column(String(10))
	filepath = 	Column(String(256))
	artist = 	Column(String(50))
	url = 		Column(String(512))
	time = 		Column(DateTime)
	width = 	Column(Integer)
	height = 	Column(Integer)
	size = 		Column(Integer)
	description = 	Column(String(256))
	score = 	Column(Integer)

	trace = 	relationship('ImageTrace')


	def __init__(self, *args, **kwargs):
		Base.__init__(self, *args, **kwargs)

		self.step = 1


	def save(self):
		dbsession = DBSession()
		dbsession.add(self)
		dbsession.commit()


	def add_trace(self, name, data):
		self.trace.append(ImageTrace(step=self.step, name=name, data=data))
		self.step += 1

