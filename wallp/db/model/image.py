from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from .base import Base
from .image_trace import ImageTrace


class Image(Base):
	__tablename__ = 'image'

	id		= Column(Integer, primary_key=True)
	type		= Column(String(10))
	filepath	= Column(String(256))
	url		= Column(String(512))
	time		= Column(Integer)
	width		= Column(Integer)
	height		= Column(Integer)
	size		= Column(Integer)
	score		= Column(Integer)
	artist		= Column(String(50))
	title		= Column(String(256))
	description	= Column(String(1024))
	context_url	= Column(String(512))
	favorite	= Column(Boolean, default=False)

	# user
	# score (source)
	# likes (local)
	# source id
	
	trace = 	relationship('ImageTrace')
	# source = 	relationship('Source')

	def __init__(self, *args, **kwargs):
		Base.__init__(self, *args, **kwargs)
		self.step = 1


	'''def save(self):
		dbsession = DBSession()
		dbsession.add(self)
		dbsession.commit()'''


	def add_trace(self, name, data):
		self.trace.append(ImageTrace(step=self.step, name=name, data=data))
		self.step += 1

