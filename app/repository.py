
from abc import ABC, abstractmethod
from pathlib import Path
from app.database import DB


class URLMapRepository(ABC):
    """ Abstract base class for repository"""
    @abstractmethod
    async def get_url_from_slug(self, slug: str) -> str | None:
        """ get url string  from slug or None if it is not in repository"""

    @abstractmethod
    async def get_slugs_from_url(self, url: str) -> set[str]:
        """ get slugs  from url """

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

    async def get_slugs_from_url(self, url: str) -> set[str]:
        return self.url_dict.get(url, set())

    async def store_url_and_slug(self, slug: str, url: str):
        self.slug_dict[slug] = url
        slugs=self.url_dict.get(url, set())
        slugs.add(slug)
        self.url_dict[url] = slugs

    async def init_repo(self):
        pass



class DatabaseURlMapRepository(URLMapRepository):
    def __init__(self, db_path) -> None:
        super().__init__()
        if db_path:
            db_url = f"sqlite+aiosqlite:////{db_path.as_posix()}"
        else:
            db_url= f"sqlite+aiosqlite://" # memory based
        self.db = DB(db_url)

    async def get_url_from_slug(self, slug: str) -> str | None:
        url_map = await self.db.get_url_map_for_slug(slug=slug)
        if url_map is None:
            return None
        return url_map.url

    async def get_slugs_from_url(self, url: str) -> set[str]:
        url_maps = await self.db.get_url_maps_for_url(url=url)
        return {url_map.slug for url_map in url_maps}

    async def store_url_and_slug(self, slug: str, url: str):
        await self.db.add_url_map(url=url, slug=slug)

    async def init_repo(self):
        await self.db.init_models()


#TOODO: allow this to be configurable
