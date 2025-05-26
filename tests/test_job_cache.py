import os
import pytest
import pytest_asyncio
from mrkutil.cache.job_cache import JobCache, AJobCache
from mrkutil.enum import JobStatusEnum

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")


@pytest.fixture(scope="function")
def job_cache():
    cache = JobCache()
    yield cache
    # Clean up all test jobs
    cache.delete_keys("testjob*")


@pytest_asyncio.fixture(scope="function")
async def ajob_cache():
    cache = AJobCache()
    yield cache
    await cache.delete_keys("testjob*")


def test_jobcache_create_and_progress(job_cache):
    key = job_cache.create_job()
    assert key
    # Set progress
    job_cache.set_progress(key, status=JobStatusEnum.COMPLETE, data={"message": "done"})
    job = job_cache.check_job(key)
    assert job["status"] == JobStatusEnum.COMPLETE
    assert job["data"]["message"] == "done"
    # Delete
    job_cache.delete(key)
    assert job_cache.check_job(key) is None


def test_jobcache_parent_child_logic(job_cache):
    parent = job_cache.create_job("testjobparent")
    child1 = job_cache.create_job(parent)
    child2 = job_cache.create_job(parent)
    # Set children to COMPLETE
    job_cache.set_progress(child1, status=JobStatusEnum.COMPLETE)
    job_cache.set_progress(child2, status=JobStatusEnum.COMPLETE)
    # Should update parent to COMPLETE
    job_cache.check_set_parent_job(parent, JobStatusEnum.COMPLETE, {"msg": "all done"})
    parent_job = job_cache.check_job(parent)
    assert parent_job["status"] == JobStatusEnum.COMPLETE
    # Set one child to FAILED
    job_cache.set_progress(child2, status=JobStatusEnum.FAILED)
    job_cache.check_set_parent_job(parent, JobStatusEnum.COMPLETE, {"msg": "all done"})
    parent_job = job_cache.check_job(parent)
    assert parent_job["status"] == JobStatusEnum.FAILED


@pytest.mark.asyncio
async def test_ajobcache_create_and_progress(ajob_cache):
    key = await ajob_cache.create_job()
    assert key
    # Set progress
    await ajob_cache.set_progress(key, status=JobStatusEnum.COMPLETE)
    job = await ajob_cache.check_job(key)
    assert job["status"] == JobStatusEnum.COMPLETE
    # Delete
    await ajob_cache.delete(key)
    job = await ajob_cache.check_job(key)
    assert job is None


@pytest.mark.asyncio
async def test_ajobcache_parent_child_logic(ajob_cache):
    parent = await ajob_cache.create_job()
    child1 = f"{parent}_child1"
    child2 = f"{parent}_child2"
    await ajob_cache.set(child1, {"status": JobStatusEnum.COMPLETE})
    await ajob_cache.set(child2, {"status": JobStatusEnum.COMPLETE})
    # Should update parent to COMPLETE
    await ajob_cache.check_set_parent_job(
        parent, JobStatusEnum.COMPLETE, {"msg": "all done"}
    )
    parent_job = await ajob_cache.check_job(parent)
    assert parent_job["status"] == JobStatusEnum.COMPLETE
    # Set one child to FAILED
    await ajob_cache.set(child2, {"status": JobStatusEnum.FAILED})
    await ajob_cache.check_set_parent_job(
        parent, JobStatusEnum.COMPLETE, {"msg": "all done"}
    )
    parent_job = await ajob_cache.check_job(parent)
    assert parent_job["status"] == JobStatusEnum.FAILED
