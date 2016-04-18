
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.schema import UniqueConstraint

from .base import Base


class Source(Base):
	__tablename__ = 'source'

	id	= Column(Integer, primary_key=True)
	name	= Column(String(64))
	enabled	= Column(Boolean)

	__table_args__ = (UniqueConstraint('name'),)

