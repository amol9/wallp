from sqlalchemy import Column, Integer, String, Boolean

from . import Base


class SearchTerm(Base):
	__tablename__ = 'search_terms'

	id = 		Column(Integer, primary_key=True)
	term = 		Column(String(100))
	enabled = 	Column(Boolean, default=True)

