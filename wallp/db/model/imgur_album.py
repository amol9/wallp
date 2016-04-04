from sqlalchemy import Column, Integer, String, Boolean, Text

from . import Base


class ImgurAlbum(Base):
	__tablename__ = 'imgur'

	id 			= Column(Integer, primary_key=True)
	album_id 		= Column(String(512))
	image_count 		= Column(Integer)
	user			= Column(String(512))
	enabled 		= Column(Boolean, default=True)
	used_image_count	= Column(Integer)
	title			= Column(String(1024))
	description		= Column(Text)
	wallpaper		= Column(Boolean, default=False)
	favorite		= Column(Boolean, default=False)

