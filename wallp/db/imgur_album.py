from sqlalchemy import Column, Integer, String, Boolean

from . import Base


class ImgurAlbum(Base):
	__tablename__ = 'imgur'

	id 		= Column(Integer, primary_key=True)
	url 		= Column(String(512))
	image_count 	= Column(Integer)
	enabled 	= Column(Boolean, default=True)

