from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from . import Base


class Image(Base):
	__tablename__ = 'images'

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

	trace = 	relationship('ImageTrace', order_by=id)

