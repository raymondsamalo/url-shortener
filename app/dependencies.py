from app.repository import InMemoryURLMapRepository, DatabaseURlMapRepository

# declare our repository -> configurable using config file
# repo = DatabaseURlMapRepository("/tmp/database.db")
repo = DatabaseURlMapRepository(db_path=None)