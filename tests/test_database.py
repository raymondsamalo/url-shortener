import pytest
import pytest_asyncio

from app.database import DB


@pytest_asyncio.fixture
async def db():
    """Create an in-memory database fixture for each async test."""
    database = DB("sqlite+aiosqlite:///:memory:")
    await database.init_models()
    try:
        yield database
    finally:
        await database._engine.dispose()


def test_db_init_initializes_engine():
    """Ensure the database engine and session factory are built correctly."""
    db = DB("sqlite+aiosqlite:///:memory:")

    assert db._url == "sqlite+aiosqlite:///:memory:"
    assert db._engine is not None
    assert db._session_maker is not None


@pytest.mark.asyncio
async def test_db_init_models_creates_table(db):
    """Verify the schema is initialized without raising an error."""
    await db.init_models()


@pytest.mark.asyncio
async def test_db_async_session_returns_session(db):
    """Ensure a new async session can be constructed and closed."""
    session = db.async_session()
    assert session is not None
    await session.close()


@pytest.mark.asyncio
async def test_db_insert_url_map_inserts_row(db):
    """Insert a mapping and confirm the row stores the expected URL and link."""
    result = await db.insert_url_map(url="https://example.com", link="abc123")

    assert result.url == "https://example.com"
    assert result.link == "abc123"


@pytest.mark.asyncio
async def test_db_update_url_for_link_updates_row(db):
    """Update a stored mapping and confirm the URL changes for the same link."""
    await db.insert_url_map(url="https://example.com", link="abc123")
    result = await db.update_url_for_link(
        url="https://example.com/updated",
        link="abc123",
    )

    assert result is not None
    assert result.url == "https://example.com/updated"
    assert result.link == "abc123"


@pytest.mark.asyncio
async def test_db_delete_url_map_for_link_removes_row(db):
    """Delete a mapping and confirm it no longer exists in the database."""
    await db.insert_url_map(url="https://example.com", link="abc123")
    result = await db.delete_url_map_for_link("abc123")

    assert result is not None
    assert result.link == "abc123"
    assert await db.get_url_map_for_link("abc123") is None


@pytest.mark.asyncio
async def test_db_get_url_map_for_link_fetches_row(db):
    """Lookup a mapping by short link and ensure the stored URL is returned."""
    await db.insert_url_map(url="https://example.com", link="abc123")
    result = await db.get_url_map_for_link("abc123")

    assert result is not None
    assert result.url == "https://example.com"
    assert result.link == "abc123"


@pytest.mark.asyncio
async def test_db_get_url_maps_for_url_fetches_rows(db):
    """Fetch all short links for a given original URL."""
    await db.insert_url_map(url="https://example.com", link="abc123")
    await db.insert_url_map(url="https://example.com", link="def456")

    result = await db.get_url_maps_for_url("https://example.com")

    assert [item.link for item in result] == ["abc123", "def456"]


@pytest.mark.asyncio
async def test_db_list_url_maps_filters_rows(db):
    """List rows using optional URL and link filters and confirm the result set matches."""
    await db.insert_url_map(url="https://example.com", link="abc123")
    await db.insert_url_map(url="https://example.org", link="def456")

    result_by_url = await db.list_url_maps(url="https://example.com", link=None)
    result_by_link = await db.list_url_maps(url=None, link="def456")

    assert [item.link for item in result_by_url] == ["abc123"]
    assert [item.link for item in result_by_link] == ["def456"]
