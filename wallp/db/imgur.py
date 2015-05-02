from sqlalchemy import Column, Integer, String, Boolean

from . import Base


class Imgur(Base):
	__tablename__ = 'imgur'

	id =		Column(Integer, primary_key=True)
	album = 	Column(String(512))
	image_count =	Column(Integer)
	enabled =	Column(Boolean, default=True)

