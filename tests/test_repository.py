import pytest

from app.repository import DatabaseURlMapRepository, InMemoryURLMapRepository


@pytest.mark.asyncio
async def test_in_memory_repository_store_and_lookup():
    repo = InMemoryURLMapRepository()

    await repo.add_new_url_and_link("short-1", "https://example.com")
    await repo.add_new_url_and_link("short-2", "https://example.com")

    assert await repo.get_url_from_link("short-1") == "https://example.com"
    assert await repo.get_links_from_url("https://example.com") == {"short-1", "short-2"}


@pytest.mark.asyncio
async def test_in_memory_repository_list_all():
    repo = InMemoryURLMapRepository()

    await repo.add_new_url_and_link("short-1", "https://example.com")
    await repo.add_new_url_and_link("short-2", "https://example.com")

    entries = await repo.list_all()

    assert {item["link"] for item in entries} == {"short-1", "short-2"}


@pytest.mark.asyncio
async def test_in_memory_repository_delete_link():
    repo = InMemoryURLMapRepository()

    await repo.add_new_url_and_link("short-1", "https://example.com")
    await repo.add_new_url_and_link("short-2", "https://example.com")

    await repo.delete_link("short-1")

    assert await repo.get_url_from_link("short-1") is None
    assert await repo.get_links_from_url("https://example.com") == {"short-2"}


@pytest.mark.asyncio
async def test_in_memory_repository_update_url_for_link():
    repo = InMemoryURLMapRepository()

    await repo.add_new_url_and_link("short-1", "https://example.com")
    await repo.add_new_url_and_link("short-2", "https://example.com")

    await repo.update_url_for_link("short-1", "https://example.org")

    assert await repo.get_url_from_link("short-1") == "https://example.org"
    assert await repo.get_links_from_url("https://example.com") == {"short-2"}
    assert await repo.get_links_from_url("https://example.org") == {"short-1"}


@pytest.mark.asyncio
async def test_database_repository_store_and_lookup(tmp_path):
    repo = DatabaseURlMapRepository(str(tmp_path / "test.db"))
    await repo.init_repo()

    await repo.add_new_url_and_link("short-1", "https://example.com")
    await repo.add_new_url_and_link("short-2", "https://example.com")

    assert await repo.get_url_from_link("short-1") == "https://example.com"
    assert await repo.get_links_from_url("https://example.com") == {"short-1", "short-2"}


@pytest.mark.asyncio
async def test_database_repository_list_all(tmp_path):
    repo = DatabaseURlMapRepository(str(tmp_path / "test.db"))
    await repo.init_repo()

    await repo.add_new_url_and_link("short-1", "https://example.com")
    await repo.add_new_url_and_link("short-2", "https://example.com")

    entries = await repo.list_all()

    assert {item["link"] for item in entries} == {"short-1", "short-2"}


@pytest.mark.asyncio
async def test_database_repository_delete_link(tmp_path):
    repo = DatabaseURlMapRepository(str(tmp_path / "test.db"))
    await repo.init_repo()

    await repo.add_new_url_and_link("short-1", "https://example.com")
    await repo.add_new_url_and_link("short-2", "https://example.com")

    await repo.delete_link("short-1")

    assert await repo.get_url_from_link("short-1") is None
    assert await repo.get_links_from_url("https://example.com") == {"short-2"}


@pytest.mark.asyncio
async def test_database_repository_update_url_for_link(tmp_path):
    repo = DatabaseURlMapRepository(str(tmp_path / "test.db"))
    await repo.init_repo()

    await repo.add_new_url_and_link("short-1", "https://example.com")
    await repo.add_new_url_and_link("short-2", "https://example.com")

    await repo.update_url_for_link("short-1", "https://example.org")

    assert await repo.get_url_from_link("short-1") == "https://example.org"
    assert await repo.get_links_from_url("https://example.com") == {"short-2"}
    assert await repo.get_links_from_url("https://example.org") == {"short-1"}
