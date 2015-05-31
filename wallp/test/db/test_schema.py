from unittest import TestCase, main as ut_main
from sqlalchemy import create_engine

from wallp.db import *


class TestSchema(TestCase):

	def test_create(self):
		engine = create_engine('sqlite:///:memory:', echo=True)
		try:
			Base.metadata.create_all(engine)
		except Exception as e:
			self.assertTrue(False, msg='schema creation failed')
			print(e.message)


if __name__ == '__main__':
	ut_main()

