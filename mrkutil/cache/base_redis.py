import redis
import redis.asyncio as aredis
import os
import json
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

    def __init__(self, key="", cache_timeout=86400):
        self.server = redis.Redis(host=os.getenv("REDIS_HOST"))
        self._key = key
        self._cache_timeout = cache_timeout

    def _setData(self, key, data):
        if self._cache_timeout:
            self.server.set(key, data, self._cache_timeout)
        else:
            self.server.set(key, data)

    def _getData(self, key):
        return self.server.get(key)

    def _delData(self, key):
        return self.server.delete(key)

    def _getMultiple(self, keys):
        return self.server.mget(keys)

    def get(self, key):
        data = self._getData("{}_{}".format(self._key, key))
        try:
            if data:
                data = json.loads(data)
        except Exception as e:
            logger.warn("Stored data is not dictionary. Exception: {}".format(str(e)))
            pass
        return data

    def get_multiple(self, keys):
        keys = [f"{self._key}_{x}" for x in keys]
        data = self._getMultiple(keys)
        try:
            if data:
                data = [json.loads(x) for x in data if x is not None]
        except Exception as e:
            logger.warn("Stored data is not dictionary. Exception: {}".format(str(e)))
            pass
        return data

    def set(self, key, data):
        if isinstance(data, dict):
            data = json.dumps(data)

        return self._setData("{}_{}".format(self._key, key), data)

    def delete(self, key):
        return self._delData("{}_{}".format(self._key, key))

    def search(self, pattern: str):
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

    def __init__(self, key="", cache_timeout=86400):
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

    async def _setData(self, key, data):
        if self._cache_timeout:
            await self.server.set(key, data, self._cache_timeout)
        else:
            await self.server.set(key, data)

    async def _getData(self, key):
        return await self.server.get(key)

    async def _delData(self, key):
        return await self.server.delete(key)

    async def _getMultiple(self, keys):
        return await self.server.mget(keys)

    async def get(self, key):
        data = await self._getData("{}_{}".format(self._key, key))
        try:
            if data:
                data = json.loads(data)
        except Exception as e:
            logger.warn("Stored data is not dictionary. Exception: {}".format(str(e)))
            pass
        return data

    async def get_multiple(self, keys):
        keys = [f"{self._key}_{x}" for x in keys]
        data = await self._getMultiple(keys)
        try:
            if data:
                data = [json.loads(x) for x in data if x is not None]
        except Exception as e:
            logger.warn("Stored data is not dictionary. Exception: {}".format(str(e)))
            pass
        return data

    async def set(self, key, data):
        if isinstance(data, dict):
            data = json.dumps(data)

        return await self._setData("{}_{}".format(self._key, key), data)

    async def delete(self, key):
        return await self._delData("{}_{}".format(self._key, key))

    async def search(self, pattern: str):
        keys = await self.server.keys(pattern=self._key + "_" + pattern)
        return [(x.decode("utf-8")).replace(self._key + "_", "") for x in keys]

    async def delete_keys(self, pattern: str):
        keys = await self.search(pattern)
        for key in keys:
            await self.delete(key)
        return len(keys)
