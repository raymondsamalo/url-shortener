
from abc import ABC, abstractmethod
from pathlib import Path
from app.database import DB


class URLMapRepository(ABC):
    """ Abstract base class for repository"""
    @abstractmethod
    async def get_url_from_slug(self, slug: str) -> str | None:
        """ get url string  from slug or None if it is not in repository"""

    @abstractmethod
    async def get_slug_from_url(self, url: str) -> str | None:
        """ get slug  from url or None if it is not in repository"""

    @abstractmethod
    async def store_url_and_slug(self, slug: str, url: str):
        """ store url and slug into repository"""

    @abstractmethod
    async def init_repo(self):
        """ handler for initialization"""


class InMemoryURLMapRepository(URLMapRepository):
    """
    simple in memory (dictionaries) repository
    """

    def __init__(self) -> None:
        super().__init__()
        self.slug_dict = {}
        self.url_dict = {}

    async def get_url_from_slug(self, slug: str) -> str | None:
        return self.slug_dict.get(slug, None)

    async def get_slug_from_url(self, url: str) -> str | None:
        return self.url_dict.get(url, None)

    async def store_url_and_slug(self, slug: str, url: str):
        self.slug_dict[slug] = url
        self.url_dict[url] = slug

    async def init_repo(self):
        pass



class DatabaseURlMapRepository(URLMapRepository):
    def __init__(self) -> None:
        super().__init__()
        base_dir = Path(__file__).resolve().parent
        db_path = base_dir / "database.db"
        print(db_path.as_posix())
        db_url = f"sqlite+aiosqlite:////{db_path.as_posix()}"
        self.db = DB(db_url)

    async def get_url_from_slug(self, slug: str) -> str | None:
        url_map = await self.db.get_url_map_for_slug(slug=slug)
        if url_map is None:
            return None
        return url_map.url

    async def get_slug_from_url(self, url: str) -> str | None:
        url_map = await self.db.get_url_map_for_url(url=url)
        if url_map is None:
            return None
        return url_map.url

    async def store_url_and_slug(self, slug: str, url: str):
        await self.db.add_url_map(url=url, slug=slug)

    async def init_repo(self):
        await self.db.init_models()


#TOODO: allow this to be configurable
repo = DatabaseURlMapRepository()