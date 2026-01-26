import os
import pytest
import pytest_asyncio
from mrkutil.cache.base_redis import RedisBase, AsyncRedisBase

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")


@pytest.fixture(scope="function")
def redis_base():
    cache = RedisBase(key="test_base")
    yield cache
    # Clean up test data
    cache.delete_keys("*")


@pytest_asyncio.fixture(scope="function")
async def async_redis_base():
    cache = AsyncRedisBase(key="test_base")
    yield cache
    # Clean up test data
    await cache.delete_keys("*")


def test_redis_base_set_get(redis_base):
    # Test dictionary data
    redis_base.set("test1", {"key": "value"})
    data = redis_base.get("test1")
    assert data["key"] == "value"

    # Test string data
    redis_base.set("test2", "hello")
    assert redis_base.get("test2") == b"hello"


def test_redis_base_delete(redis_base):
    redis_base.set("test_del", {"data": "to_delete"})
    assert redis_base.get("test_del") is not None
    redis_base.delete("test_del")
    assert redis_base.get("test_del") is None


def test_redis_base_search(redis_base):
    redis_base.set("search1", {"data": 1})
    redis_base.set("search2", {"data": 2})
    redis_base.set("other", {"data": 3})

    search_results = redis_base.search("search*")
    assert len(search_results) == 2
    assert "search1" in search_results
    assert "search2" in search_results


def test_redis_base_get_multiple(redis_base):
    redis_base.set("multi1", {"data": 1})
    redis_base.set("multi2", {"data": 2})

    results = redis_base.get_multiple(["multi1", "multi2"])
    assert len(results) == 2
    assert results[0]["data"] == 1
    assert results[1]["data"] == 2


@pytest.mark.asyncio
async def test_async_redis_base_set_get(async_redis_base):
    # Test dictionary data
    await async_redis_base.set("test1", {"key": "value"})
    data = await async_redis_base.get("test1")
    assert data["key"] == "value"

    # Test string data
    await async_redis_base.set("test2", "hello")
    assert await async_redis_base.get("test2") == b"hello"


@pytest.mark.asyncio
async def test_async_redis_base_delete(async_redis_base):
    await async_redis_base.set("test_del", {"data": "to_delete"})
    assert await async_redis_base.get("test_del") is not None
    await async_redis_base.delete("test_del")
    assert await async_redis_base.get("test_del") is None


@pytest.mark.asyncio
async def test_async_redis_base_search(async_redis_base):
    await async_redis_base.set("search1", {"data": 1})
    await async_redis_base.set("search2", {"data": 2})
    await async_redis_base.set("other", {"data": 3})

    search_results = await async_redis_base.search("search*")
    assert len(search_results) == 2
    assert "search1" in search_results
    assert "search2" in search_results


@pytest.mark.asyncio
async def test_async_redis_base_get_multiple(async_redis_base):
    await async_redis_base.set("multi1", {"data": 1})
    await async_redis_base.set("multi2", {"data": 2})

    results = await async_redis_base.get_multiple(["multi1", "multi2"])
    assert len(results) == 2
    assert results[0]["data"] == 1
    assert results[1]["data"] == 2
