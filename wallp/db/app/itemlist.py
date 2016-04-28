
from sqlalchemy.sql.expression import func, select
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from ..dbsession import DBSession


class ItemListError(Exception):
	pass


class ItemList:
	item_name 	= None
	table 		= None
	item_col 	= None
	exc_cls 	= None

	def __init__(self):
		assert(self.item_name and self.table and self.item_col and self.exc_cls)

		self._db_session = DBSession()


	def random(self):
		item = self._db_session.query(self.table).filter(self.table.enabled == True).order_by(func.random()).first()
		item or self.raise_exc('no usable %s in list'%self.item_name)
		return getattr(item, self.item_col, None)


	def add(self, item, enabled=True, ex_values={}, commit=True):
		ex_values[self.item_col] = item
		ex_values['enabled'] = enabled

		record = self.table(**ex_values)
		try:
			self._db_session.add(record)
			self.commit(commit)
		except IntegrityError as e:
			self.raise_exc('%s: %s, already present'%(self.item_name, item))



	def commit(self, commit=True):
		commit and self._db_session.commit()


	def raise_exc(self, msg):
		raise self.exc_cls(msg)


	def remove(self, item, commit=True):
		count = self._db_session.query(self.table).filter_by(**{self.item_col: item}).delete()
		self.check_count_and_commit(item, count, commit)


	def check_count_and_commit(self, item, count, commit=True):
		if count == 0:
			self.raise_exc('%s: %s, not found'%(self.item_name, item))
		else:
			self.commit()


	def enable(self, item, commit=True):
		count = self._db_session.query(self.table).filter_by(**{self.item_col: item}).update({'enabled': True})
		self.check_count_and_commit(item, count, commit)


	def disable(self, item, commit=True):
		count = self._db_session.query(self.table).filter_by(**{self.item_col: item}).update({'enabled': False})
		self.check_count_and_commit(item, count, commit)


	def exists(self, item):
		return self._db_session.query(self.table).filter_by(**{self.item_col: item}).count() > 0	


	def get_all(self):
		return self._db_session.query(self.table).all()

