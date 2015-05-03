from sqlalchemy import Column, Integer, String

from . import Base


class Config(Base):
	__tablename__ = 'config'

	group =	Column(String(20), primary_key=True)
	name =	Column(String(40), primary_key=True)
	value =	Column(String(512))
	type = 	Column(String(15))

