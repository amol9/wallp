
from wallp.db.create_db import CreateDB


def create_db(db_path):
	cd = CreateDB(db_path=db_path)
	cd.execute()

