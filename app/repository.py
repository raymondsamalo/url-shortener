
from abc import ABC, abstractmethod
from pathlib import Path
from app.database import DB


class URLMapRepository(ABC):
    """ Abstract base class for repository"""
    @abstractmethod
    async def get_url_from_link(self, link: str) -> str | None:
        """ get url string  from link or None if it is not in repository"""

    @abstractmethod
    async def get_links_from_url(self, url: str) -> set[str]:
        """ get links  from url """

    @abstractmethod
    async def store_url_and_link(self, link: str, url: str):
        """ store url and link into repository"""

    @abstractmethod
    async def init_repo(self):
        """ handler for initialization"""

    @abstractmethod
    async def list_all(self, link: str|None=None, url: str|None =None) -> list[dict]:
        """ list all """



class InMemoryURLMapRepository(URLMapRepository):
    """
    simple in memory (dictionaries) repository
    """

    def __init__(self) -> None:
        super().__init__()
        self.link_dict = {}
        self.url_dict = {}

    async def get_url_from_link(self, link: str) -> str | None:
        return self.link_dict.get(link, None)

    async def get_links_from_url(self, url: str) -> set[str]:
        return self.url_dict.get(url, set())

    async def store_url_and_link(self, link: str, url: str):
        self.link_dict[link] = url
        links=self.url_dict.get(url, set())
        links.add(link)
        self.url_dict[url] = links

    async def init_repo(self):
        pass

    async def list_all(self, link: str|None=None, url: str|None =None)  -> list[dict]:
        return [{"link":link, "url":url, "id":"", "created":"" } for link, url in self.link_dict.items()]



class DatabaseURlMapRepository(URLMapRepository):
    def __init__(self, db_path) -> None:
        super().__init__()
        if db_path:
            db_url = f"sqlite+aiosqlite:////{db_path}"
        else:
            db_url= f"sqlite+aiosqlite://" # memory based
        self.db = DB(db_url)

    async def get_url_from_link(self, link: str) -> str | None:
        url_map = await self.db.get_url_map_for_link(link=link)
        if url_map is None:
            return None
        return url_map.url

    async def get_links_from_url(self, url: str) -> set[str]:
        url_maps = await self.db.get_url_maps_for_url(url=url)
        return {url_map.Link for url_map in url_maps}

    async def store_url_and_link(self, link: str, url: str):
        await self.db.add_url_map(url=url, link=link)

    async def list_all(self, link: str|None=None, url: str|None =None) -> list[dict]:
        results=await self.db.list_url_maps(url=url, link=link)
        return [{"link":result.Link, "url":result.url, "id":result.id, "created":result.created_at } for result in results]

    async def init_repo(self):
        await self.db.init_models()


#TOODO: allow this to be configurable
