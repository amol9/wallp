from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.schema import UniqueConstraint

from .base import Base


class Query(Base):
	__tablename__ = 'query'

	id 		= Column(Integer, primary_key=True)
	term 		= Column(String(100))
	enabled 	= Column(Boolean, default=True)
	use_count	= Column(Integer)

	__table_args__ = (UniqueConstraint('term'),)


