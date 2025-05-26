from mrkutil.utilities import random_uuid
from .base_redis import RedisBase, AsyncRedisBase
from mrkutil.enum import JobStatusEnum


class JobCache(RedisBase):
    def __init__(self):
        super().__init__(key="u_jobs", cache_timeout=3600)

    def create_job(self, parent_key: str = None):
        key = random_uuid()
        if parent_key:
            key = f"{parent_key}_{key}"
        self.set(key, {"status": JobStatusEnum.PENDING})
        return key

    def set_progress(
        self,
        key: str,
        status: JobStatusEnum = JobStatusEnum.IN_PROGRESS,
        data: dict = {},
    ):
        self.set(key, {"status": status, "data": data})

    def check_job(self, key: str):
        return self.get(key)

    def check_set_parent_job(self, key: str, status: JobStatusEnum, data: dict):
        job = self.get(key)
        if job:
            keys = self.search(pattern=f"{key}_*")
            children = self.get_multiple(keys)
            if all(item.get("status") == JobStatusEnum.COMPLETE for item in children):
                self.set_progress(key, status, data)
            elif any(item.get("status") == JobStatusEnum.FAILED for item in children):
                self.set_progress(key, JobStatusEnum.FAILED)


class AJobCache(AsyncRedisBase):
    def __init__(self):
        super().__init__(key="u_jobs", cache_timeout=3600)

    async def create_job(self):
        key = random_uuid()
        await self.set(key, {"status": JobStatusEnum.PENDING})
        return key

    async def set_progress(self, key: str, status: JobStatusEnum, data: dict = {}):
        await self.set(key, {"status": status, "data": data})

    async def check_job(self, key: str):
        job = await self.get(key)
        return job

    async def check_set_parent_job(self, key: str, status: JobStatusEnum, data: dict):
        job = await self.get(key)
        if job:
            keys = await self.search(pattern=f"{key}_*")
            children = await self.get_multiple(keys)
            if all(item.get("status") == JobStatusEnum.COMPLETE for item in children):
                await self.set_progress(key, status, data)
            elif any(item.get("status") == JobStatusEnum.FAILED for item in children):
                await self.set_progress(key, JobStatusEnum.FAILED)
