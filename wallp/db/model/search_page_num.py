from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import UniqueConstraint

from .base import Base


class SearchPageNum(Base):
	__tablename__ = 'search_page_num'

	id 	= Column(Integer, primary_key=True)
	group 	= Column(String(20))
	name 	= Column(String(40))
	value   = Column(String(512))
	type 	= Column(String(15))

	__table_args__ = (UniqueConstraint('group', 'name'),)

