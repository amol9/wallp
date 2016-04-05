from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.schema import UniqueConstraint

from .base import Base


class Subreddit(Base):
	__tablename__ = 'subreddit'

	id = 		Column(Integer, primary_key=True)
	name = 		Column(String(256))
	enabled = 	Column(Boolean, default=True)

	__table_args__ = (UniqueConstraint('name'),)

