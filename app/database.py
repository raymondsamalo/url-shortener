import os
from sqlite3 import IntegrityError
import uuid
from datetime import datetime
from sqlalchemy import StaticPool, String, insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import select, DateTime, func
from app.util.logger import get_module_logger
logger = get_module_logger(__name__)
Base = declarative_base()


class URLMap(Base):
    """
    Map url to link
    """
    __tablename__ = "url_map"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(String, index=True)
    link: Mapped[str] = mapped_column(String, unique=True, index=True)
    # Automatically set when the record is created
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now()
    )

    # Automatically updated whenever the record changes
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        onupdate=func.now()
    )


class DB:
    def __init__(self, database_url) -> None:
        self._url = database_url
        self._engine = create_async_engine(self._url,  connect_args={
            "check_same_thread": False},  poolclass=StaticPool, echo=True)
        self._session_maker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine)

    async def init_models(self):
        async with self._engine.begin() as conn:
            # Avoid dropping tables in production!
            # await conn.run_sync(Base.metadata.drop_all)
            # This safely executes the synchronous DDL function code asynchronously
            await conn.run_sync(Base.metadata.create_all)

    def async_session(self):
        return self._session_maker()

    async def add_url_map(self, url: str, link: str) -> URLMap:
        async with self.async_session() as session:
            stmt = insert(URLMap).values(url=url, link=link).returning(URLMap)
            try:
                result = await session.execute(stmt)
                await session.commit()
            except IntegrityError:
                logger.error("Failed to insert %s -> %s ",
                             url, link, exc_info=1)
                await session.rollback()
                raise
            return result.scalar_one()

    async def get_url_map_for_link(self, link: str) -> URLMap:
        async with self.async_session() as session:
            stmt = select(URLMap).where(URLMap.link == link)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_url_maps_for_url(self, url: str) -> list[URLMap]:
        async with self.async_session() as session:
            stmt = select(URLMap).where(URLMap.url == url)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def list_url_maps(self, url: str|None, link:str|None) -> list[URLMap]:
        async with self.async_session() as session:
            stmt = select(URLMap)
            if url:
                stmt = stmt.where(URLMap.url == url)
            if link:
                stmt = stmt.where(URLMap.link == link)
            stmt=stmt.order_by(URLMap.created_at)
            result = await session.execute(stmt)
            return list(result.scalars().all())
