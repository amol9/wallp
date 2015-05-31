from sqlalchemy import Column, Integer, String, Boolean

from . import Base


class Reddit(Base):
	__tablename__ = 'reddit'

	id = 		Column(Integer, primary_key=True)
	sub = 		Column(String(70))
	enabled = 	Column(Boolean, default=True)

