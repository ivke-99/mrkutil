import pytest
from sqlalchemy import create_engine, select, Table, Column, Integer, MetaData
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    Session,
    DeclarativeBase,
    MappedAsDataclass,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from mrkutil.pagination.sqlalchemy import paginate, apaginate
from mrkutil.utilities.sqlalchemy_mixins import IdMixin, CreatedMixin


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Item(Base, IdMixin, CreatedMixin):
    __tablename__ = "items"
    name: Mapped[str] = mapped_column()
    value: Mapped[int] = mapped_column()


DB_URL = "postgresql+psycopg://test_user:test_password@localhost:5432/test_db"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    session = Session(engine)
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_items(session):
    session.query(Item).delete()  # Clean up before adding
    items = [Item(name=f"item{i}", value=i) for i in range(1, 11)]
    session.add_all(items)
    session.commit()
    return items


def test_paginate_basic(session, sample_items):
    query = select(Item)
    result = paginate(query=query, session=session, page_number=1, page_size=3)
    assert result["page"] == 1
    assert result["size"] == 3
    assert result["total"] == 10
    assert len(result["items"]) == 3
    assert isinstance(result["items"][0], dict)


def test_paginate_second_page(session, sample_items):
    query = select(Item)
    result = paginate(query=query, session=session, page_number=2, page_size=4)
    assert result["page"] == 2
    assert result["size"] == 4
    assert result["total"] == 10
    assert len(result["items"]) == 4
    assert result["items"][0]["name"] == "item5"


def test_paginate_sorting_desc(session, sample_items):
    query = select(Item)
    result = paginate(
        query=query,
        session=session,
        page_number=1,
        page_size=5,
        direction="desc",
        sort_by="value",
    )
    values = [item["value"] for item in result["items"]]
    assert values == sorted(values, reverse=True)


def test_paginate_format_to_dict(session, sample_items):
    query = select(Item)
    result = paginate(
        query=query, session=session, page_number=1, page_size=2, format_to_dict=True
    )
    assert isinstance(result["items"][0], dict)
    assert set(result["items"][0].keys()) >= {"id", "name", "value", "created_at"}


def test_paginate_use_scalars_false(session, sample_items):
    query = select(Item.id, Item.name)
    result = paginate(
        query=query, session=session, page_number=1, page_size=2, use_scalars=False
    )
    assert set(result["items"][0].keys()) == {"id", "name"}


def test_paginate_empty_result(session):
    query = select(Item).where(Item.value > 1000)
    result = paginate(query=query, session=session, page_number=1, page_size=2)
    assert result["total"] == 0
    assert result["items"] == []


def test_paginate_out_of_range_page(session, sample_items):
    query = select(Item)
    result = paginate(query=query, session=session, page_number=100, page_size=5)
    assert result["items"] == []


@pytest.mark.asyncio
async def test_apaginate_basic():
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        # Clean up before inserting
        await session.execute(Item.__table__.delete())
        await session.commit()
        # Insert items
        async with session.begin():
            session.add_all([Item(name=f"aitem{i}", value=i) for i in range(1, 6)])
        query = select(Item)
        result = await apaginate(
            query=query, session=session, page_number=None, page_size=2
        )
        assert result["page"] == 1
        assert result["size"] == 2
        assert result["total"] == 5
        assert len(result["items"]) == 2
        assert isinstance(result["items"][0], dict)
    await engine.dispose()


def test_paginate_negative_page_size(session, sample_items):
    query = select(Item)
    with pytest.raises(Exception) as excinfo:
        paginate(query=query, session=session, page_number=1, page_size=-1)
    assert "Page size should not be negative" in str(excinfo.value)


def test_paginate_negative_page_number(session, sample_items):
    query = select(Item)
    with pytest.raises(Exception) as excinfo:
        paginate(query=query, session=session, page_number=-1, page_size=2)
    assert "Page number should be positive" in str(excinfo.value)


def test_paginate_deprecated_params(session, sample_items):
    query = select(Item)
    # recurse and format_to_dict are deprecated but should not break
    result = paginate(
        query=query,
        session=session,
        page_number=1,
        page_size=2,
        recurse=True,
        format_to_dict=True,
    )
    assert len(result["items"]) == 2


def test_paginate_no_unique_column_warns(session, caplog):
    # Create a table with no unique or primary key columns
    metadata = MetaData()
    temp_table = Table("temp", metadata, Column("val", Integer))
    metadata.create_all(session.get_bind())
    session.execute(temp_table.insert().values(val=1))
    session.commit()
    query = select(temp_table)
    with caplog.at_level("WARNING"):
        paginate(
            query=query,
            session=session,
            page_number=None,
            page_size=1,
            format_to_dict=False,
        )
    assert (
        "no unique column" in caplog.text
        or "Pagination may yield inconsistent results" in caplog.text
    )


def test_paginate_no_results_page_size_none(session):
    query = select(Item).where(Item.value > 1000)
    result = paginate(query=query, session=session, page_number=1, page_size=None)
    assert result["total"] == 0
    assert result["items"] == []


def test_paginate_page_size_larger_than_total(session, sample_items):
    query = select(Item)
    result = paginate(query=query, session=session, page_number=1, page_size=100)
    assert result["size"] == 10
    assert len(result["items"]) == 10


def test_paginate_sort_by_nonexistent_column_warns(session, sample_items, caplog):
    query = select(Item)
    with caplog.at_level("WARNING"):
        paginate(
            query=query,
            session=session,
            page_number=1,
            page_size=100,
            sort_by="doesnotexist",
        )
    # Should not crash, but should warn (or at least not sort)
