from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from .base import Base


class ImageTrace(Base):
	__tablename__ = 'image_trace'

	id = 		Column(Integer, primary_key=True)
	step =		Column(Integer)
	name = 		Column(String(50))
	data = 		Column(String(512))
	image_id = 	Column(Integer, ForeignKey('image.id'))

	#image = 	relationship('Image', backref='image')
