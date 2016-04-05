from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import UniqueConstraint

from .base import Base


class Config(Base):
	__tablename__ = 'config2'

	id 	= Column(Integer, primary_key=True)
	name 	= Column(String(128), nullable=False)
	value   = Column(String(512))
	type 	= Column(String(15))

	__table_args__ = (UniqueConstraint('name'),)

