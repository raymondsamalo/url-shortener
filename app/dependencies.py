import os
import sqlite3
from app.repository import InMemoryURLMapRepository, DatabaseURlMapRepository
import pathlib
# Finds the absolute directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = pathlib.Path(BASE_DIR).parent.joinpath("database.db").resolve().as_posix()
print(db_path)
# declare our repository -> configurable using config file in future
repo = DatabaseURlMapRepository(db_path)
# repo = DatabaseURlMapRepository(db_path=None)