import redis
import redis.asyncio as aredis
import os
import orjson
import logging

logger = logging.getLogger(__name__)


class RedisBase:
    """Data structure store

    RedisBase is a class that provides methods for storing and retrieving data
    using Redis as the underlying database. It allows saving and reading messages
    received from other services.

    Attributes:
        server (redis.Redis): The Redis server instance.
        _key (str): The key prefix used for storing data.
        _cache_timeout (int): The cache timeout value in seconds.

    """

    def __init__(self, key: str = "", cache_timeout: int = 86400):
        self.server = redis.Redis(host=os.getenv("REDIS_HOST"))
        self._key = key
        self._cache_timeout = cache_timeout

    def _setData(self, key: str, data: dict):
        if self._cache_timeout:
            self.server.set(key, data, self._cache_timeout)
        else:
            self.server.set(key, data)

    def _getData(self, key: str):
        return self.server.get(key)

    def _delData(self, key: str):
        return self.server.delete(key)

    def _getMultiple(self, keys: list[str]):
        return self.server.mget(keys)

    def get(self, key: str):
        data = self._getData("{}_{}".format(self._key, key))
        try:
            if data:
                data = orjson.loads(data)
        except Exception as e:
            logger.warning(
                "Stored data is not dictionary. Exception: {}".format(str(e))
            )
            pass
        return data

    def get_multiple(self, keys: list[str]):
        keys = [f"{self._key}_{x}" for x in keys]
        data = self._getMultiple(keys)
        try:
            if data:
                data = [orjson.loads(x) for x in data if x is not None]
        except Exception as e:
            logger.warning(
                "Stored data is not dictionary. Exception: {}".format(str(e))
            )
            pass
        return data

    def set(self, key: str, data: dict):
        if isinstance(data, dict):
            data = orjson.dumps(data)

        return self._setData("{}_{}".format(self._key, key), data)

    def delete(self, key: str):
        return self._delData("{}_{}".format(self._key, key))

    def search(self, pattern: str) -> list[str]:
        keys = self.server.keys(pattern=self._key + "_" + pattern)
        return [(x.decode("utf-8")).replace(self._key + "_", "") for x in keys]

    def delete_keys(self, pattern: str):
        keys = self.search(pattern)
        for key in keys:
            self.delete(key)
        return len(keys)


class AsyncRedisBase:
    """Data structure store

    RedisBase is a class that provides methods for storing and retrieving data
    using Redis as the underlying database. It allows saving and reading messages
    received from other services.

    Attributes:
        server (redis.Redis): The Redis server instance.
        _key (str): The key prefix used for storing data.
        _cache_timeout (int): The cache timeout value in seconds.

    """

    def __init__(self, key: str = "", cache_timeout: int = 86400):
        self.server = aredis.Redis(host=os.getenv("REDIS_HOST"))
        self._key = key
        self._cache_timeout = cache_timeout

    def __del__(self):
        # Close connection when this object is destroyed
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.server.aclose())
            else:
                loop.run_until_complete(self.server.aclose())
        except Exception:
            pass

    async def _setData(self, key: str, data: dict):
        if self._cache_timeout:
            await self.server.set(key, data, self._cache_timeout)
        else:
            await self.server.set(key, data)

    async def _getData(self, key: str):
        return await self.server.get(key)

    async def _delData(self, key: str):
        return await self.server.delete(key)

    async def _getMultiple(self, keys: list[str]):
        return await self.server.mget(keys)

    async def get(self, key: str):
        data = await self._getData("{}_{}".format(self._key, key))
        try:
            if data:
                data = orjson.loads(data)
        except Exception as e:
            logger.warning(
                "Stored data is not dictionary. Exception: {}".format(str(e))
            )
            pass
        return data

    async def get_multiple(self, keys: list[str]):
        keys = [f"{self._key}_{x}" for x in keys]
        data = await self._getMultiple(keys)
        try:
            if data:
                data = [orjson.loads(x) for x in data if x is not None]
        except Exception as e:
            logger.warning(
                "Stored data is not dictionary. Exception: {}".format(str(e))
            )
            pass
        return data

    async def set(self, key: str, data: dict):
        if isinstance(data, dict):
            data = orjson.dumps(data)

        return await self._setData("{}_{}".format(self._key, key), data)

    async def delete(self, key: str):
        return await self._delData("{}_{}".format(self._key, key))

    async def search(self, pattern: str) -> list[str]:
        keys = await self.server.keys(pattern=self._key + "_" + pattern)
        return [(x.decode("utf-8")).replace(self._key + "_", "") for x in keys]

    async def delete_keys(self, pattern: str) -> int:
        keys = await self.search(pattern)
        for key in keys:
            await self.delete(key)
        return len(keys)
