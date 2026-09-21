
from abc import ABC, abstractmethod
from app.database import DB
import asyncio


class URLMapRepository(ABC):
    """ Abstract base class for repository"""
    @abstractmethod
    async def get_url_from_link(self, link: str) -> str | None:
        """ get url string  from link or None if it is not in repository"""

    @abstractmethod
    async def get_links_from_url(self, url: str) -> set[str]:
        """ get links  from url """

    @abstractmethod
    async def add_new_url_and_link(self, link: str, url: str):
        """ store new url and link into repository"""

    @abstractmethod
    async def update_url_for_link(self, link: str, url: str):
        """ update url for link"""

    @abstractmethod
    async def delete_link(self, link: str):
        """ delete link """

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
        self.lock = asyncio.Lock()

    async def get_url_from_link(self, link: str) -> str | None:
        url = None
        async with self.lock:
            url = self.link_dict.get(link, None)
        return url
    
    async def get_links_from_url(self, url: str) -> set[str]:
        links = None
        async with self.lock:
            links = self.url_dict.get(url, set())
        return links

    async def add_new_url_and_link(self, link: str, url: str):
        async with self.lock:
            self.link_dict[link] = url
            links=self.url_dict.get(url, set())
            links.add(link)
            self.url_dict[url] = links

    async def delete_link(self, link: str):
        async with self.lock:
            url = self.link_dict.pop(link, None)
            if url is None:
                return
            links = self.url_dict.get(url, set())
            links.discard(link)
            if links:
                self.url_dict[url] = links
            else:
                self.url_dict.pop(url, None)

    async def init_repo(self):
        pass

    async def list_all(self, link: str|None=None, url: str|None =None)  -> list[dict]:
        async with self.lock:
            all_entries = [{"link":link, "url":url, "id":"", "created":"" } for link, url in self.link_dict.items()]
        return all_entries

    async def update_url_for_link(self, link: str, url: str):
        async with self.lock:
            old_url = self.link_dict.pop(link, None)
            if old_url == url:
                return
            # update new url
            self.link_dict[link] = url
            # remove link from old url    
            links=self.url_dict.get(old_url, set())
            links.discard(link)
            if links:
                self.url_dict[old_url] = links
            else:
                self.url_dict.pop(old_url, None)
            # track link for new url
            links=self.url_dict.get(url, set())
            links.add(link)
            self.url_dict[url] = links
 
                






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
        return {url_map.link for url_map in url_maps}

    async def add_new_url_and_link(self, link: str, url: str):
        await self.db.insert_url_map(url=url, link=link)

    async def delete_link(self, link: str):
        await self.db.delete_url_map_for_link(link=link)

    async def list_all(self, link: str|None=None, url: str|None =None) -> list[dict]:
        results=await self.db.list_url_maps(url=url, link=link)
        return [{"link": result.link, "url": result.url,  "created": result.created_at} for result in results]

    async def init_repo(self):
        await self.db.init_models()

    async def update_url_for_link(self, link: str, url: str):
        await self.db.update_url_for_link(link=link, url=url)



#TOODO: allow this to be configurable
