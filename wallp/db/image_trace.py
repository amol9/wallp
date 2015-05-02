from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from . import Base


class ImageTrace(Base):
	__tablename__ = 'image_trace'

	id = 		Column(Integer, primary_key=True)
	name = 		Column(String(50))
	data = 		Column(String(512))
	image_id = 	Column(Integer, ForeignKey('images.id'))

	image = 	relationship('Image', backref='image')
