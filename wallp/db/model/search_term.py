from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.schema import UniqueConstraint

from .base import Base


class SearchTerm(Base):
	__tablename__ = 'search_term'

	id = 		Column(Integer, primary_key=True)
	term = 		Column(String(100))
	enabled = 	Column(Boolean, default=True)

	__table_args__ = (UniqueConstraint('term'),)

