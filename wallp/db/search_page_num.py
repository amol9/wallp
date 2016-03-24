from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import UniqueConstraint

from . import Base


class SearchPageNum(Base):
	__tablename__ = 'search_page_num'

	id 	= Column(Integer, primary_key=True)
	group 	= Column(String(20))
	name 	= Column(String(40))
	page   	= Column(Integer, default=0)

	__table_args__ = (UniqueConstraint('group', 'name'),)

