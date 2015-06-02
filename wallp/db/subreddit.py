from sqlalchemy import Column, Integer, String, Boolean

from . import Base


class Subreddit(Base):
	__tablename__ = 'reddit'

	id = 		Column(Integer, primary_key=True)
	name = 		Column(String(70))
	enabled = 	Column(Boolean, default=True)

