from unittest import TestCase, main as ut_main
from sqlalchemy import create_engine

from wallp.db.model.all import Base


class TestSchema(TestCase):
	db_path = 'test.db'

	def test_create(self):
		engine = create_engine('sqlite:///' + self.db_path, echo=True)
		try:
			Base.metadata.create_all(engine)
		except Exception as e:
			self.assertTrue(False, msg='schema creation failed')
			print(e.message)


if __name__ == '__main__':
	ut_main()

