import os
from sqlite3 import IntegrityError
import uuid
from datetime import datetime
from sqlalchemy import StaticPool, String, delete, insert, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import select, DateTime, func
from app.util.logger import get_module_logger

logger = get_module_logger(__name__)
Base = declarative_base()


class URLMap(Base):
    """Represent the mapping between a source URL and its shortened link."""

    __tablename__ = "url_map"
    ## at first we consider to use uuid as primary key as it is standard practice which allow us to update short url for a long url
    ## however, as we developing this take home assignment, we realize this is redudant
    # id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # link: Mapped[str] = mapped_column(String, unique=True, index=True)
    url: Mapped[str] = mapped_column(String, index=True)
    link: Mapped[str] = mapped_column(String, primary_key=True)
    # Automatically set when the record is created
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now()
    )

    # Automatically updated whenever the record changes
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        onupdate=func.now(),
    )


class DB:
    """Database wrapper used to create and query URL-to-link mappings."""

    @staticmethod
    def _copy_url_map(item: URLMap | None) -> URLMap | None:
        """Return a detached copy of a URLMap so it stays readable after session closure."""
        if item is None:
            return None
        return URLMap(
            url=item.url,
            link=item.link,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    def __init__(self, database_url) -> None:
        """Initialize the database engine and session factory for the given URL."""
        self._url = database_url
        self._engine = create_async_engine(
            self._url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=True,
        )
        self._session_maker = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )

    async def init_models(self):
        """Create the URL map table if it does not already exist."""
        async with self._engine.begin() as conn:
            # Avoid dropping tables in production!
            # await conn.run_sync(Base.metadata.drop_all)
            # This safely executes the synchronous DDL function code asynchronously
            await conn.run_sync(Base.metadata.create_all)

    def async_session(self):
        """Return a new asynchronous SQLAlchemy session for database work."""
        return self._session_maker()

    async def insert_url_map(self, url: str, link: str) -> URLMap:
        """Insert a new URL-to-link mapping and return the stored row."""
        async with self.async_session() as session:
            stmt = insert(URLMap).values(url=url, link=link).returning(URLMap)
            try:
                result = await session.execute(stmt)
                item = result.scalar_one()
                detached = self._copy_url_map(item)
                await session.commit()
            except IntegrityError:
                logger.error("Failed to insert %s -> %s ", url, link, exc_info=True)
                await session.rollback()
                raise
            return detached

    async def update_url_for_link(self, url: str, link: str) -> URLMap | None:
        """Update the URL associated with an existing short link, if present."""
        async with self.async_session() as session:
            stmt = (
                update(URLMap)
                .where(URLMap.link == link)
                .values(url=url)
                .returning(URLMap)
            )
            try:
                result = await session.execute(stmt)
                item = result.scalar_one_or_none()
                detached = self._copy_url_map(item)
                await session.commit()
            except IntegrityError:
                logger.error("Failed to update %s -> %s ", url, link, exc_info=True)
                await session.rollback()
                raise
            return detached

    async def delete_url_map_for_link(self, link: str) -> URLMap | None:
        """Delete the mapping for a short link and return the removed record, if any."""
        async with self.async_session() as session:
            stmt = delete(URLMap).where(URLMap.link == link).returning(URLMap)
            try:
                result = await session.execute(stmt)
                item = result.scalar_one_or_none()
                detached = self._copy_url_map(item)
                await session.commit()
            except IntegrityError:
                logger.error("Failed to delete %s ", link, exc_info=True)
                await session.rollback()
                raise
            return detached

    async def get_url_map_for_link(self, link: str) -> URLMap | None:
        """Fetch the row for the given shortened link, if it exists."""
        async with self.async_session() as session:
            stmt = select(URLMap).where(URLMap.link == link)
            result = await session.execute(stmt)
            item = result.scalar_one_or_none()
            return self._copy_url_map(item)

    async def get_url_maps_for_url(self, url: str) -> list[URLMap]:
        """Return all link mappings registered under the provided long URL."""
        async with self.async_session() as session:
            stmt = select(URLMap).where(URLMap.url == url)
            result = await session.execute(stmt)
            items = list(result.scalars().all())
            return [self._copy_url_map(item) for item in items]

    async def list_url_maps(self, url: str | None, link: str | None) -> list[URLMap]:
        """List URL mappings filtered by optional URL and/or short link values."""
        async with self.async_session() as session:
            stmt = select(URLMap)
            if url:
                stmt = stmt.where(URLMap.url == url)
            if link:
                stmt = stmt.where(URLMap.link == link)
            stmt = stmt.order_by(URLMap.created_at)
            result = await session.execute(stmt)
            items = list(result.scalars().all())
            return [self._copy_url_map(item) for item in items]
