import dataclasses
import logging
from typing import Optional
from sqlalchemy import select, func, desc, Select, inspect, asc, RowMapping
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


def paginate(
    query: Select,
    session: Session,
    recurse: bool = True,
    page_number: int = None,
    page_size: int = None,
    direction: str = None,
    sort_by: str = None,
    format_to_dict: bool = True,
    use_scalars: bool = True,
):
    """Apply pagination to a SQLAlchemy query object.
    :param query:
        SQLAlchemy Select object.
    :param session:
        SQLAlchemy Session object.
    :param page_number:
        Page to be returned (starts and defaults to 1).
    :param recurse:
        DEPRECATED
        to_dict implemented recursion in the past, this will not be supported soon.
    :param page_size:
        Maximum number of results to be returned in the page (defaults
        to the total results).
    :param direction:
        Direction of ordering, asc or desc
    :param sort_by:
        Column for sorting
    :param format_to_dict:
        DEPRECATED
        Wether to use to_dict method or not. Will be removed soon
    :param use_scalars:
        Wether to use mappings or sqlalchemy scalars method. If you
        are paginating a non-model query you will usually have to set this to False
    :returns:
        A dict with items (SQLAlchemy objects or dictionary objects),
        page number, desired page size, total number of results
    Basic usage::
        object = paginate(select([User]), session, 1, 10, "asc", "email")
    """
    total_results = session.scalar(select(func.count()).select_from(query.subquery()))

    query = _sort_by(query, direction, sort_by)

    query = _limit(query, page_size)

    # Page size defaults to total results
    if page_size is None or (page_size > total_results and total_results > 0):
        page_size = total_results

    query = _offset(query, page_number, page_size)

    # Page number defaults to 1
    if page_number is None:
        page_number = 1
    if use_scalars:
        results = session.scalars(query).all()
    else:
        results = session.execute(query).mappings().all()

    if format_to_dict:
        if results and isinstance(results[0], RowMapping):
            results = [dict(k) for k in results]
        else:
            results = [dataclasses.asdict(k) for k in results]
    return {
        "items": results,
        "page": page_number,
        "size": page_size,
        "total": total_results,
    }


async def apaginate(
    query: Select,
    session: AsyncSession,
    recurse: bool = True,
    page_number: int = None,
    page_size: int = None,
    direction: str = None,
    sort_by: str = None,
    format_to_dict: bool = True,
    use_scalars: bool = True,
):
    """Apply pagination to a SQLAlchemy query object.
    :param query:
        SQLAlchemy Select object.
    :param session:
        SQLAlchemy Session object.
    :param page_number:
        Page to be returned (starts and defaults to 1).
    :param recurse:
        DEPRECATED
        to_dict implemented recursion in the past, this will not be supported soon.
    :param page_size:
        Maximum number of results to be returned in the page (defaults
        to the total results).
    :param direction:
        Direction of ordering, asc or desc
    :param sort_by:
        Column for sorting
    :param format_to_dict:
        DEPRECATED
        Wether to use to_dict method or not. Will be removed soon
    :param use_scalars:
        Wether to use mappings or sqlalchemy scalars method. If you
        are paginating a non-model query you will usually have to set this to False
    :returns:
        A dict with items (SQLAlchemy objects or dictionary objects),
        page number, desired page size, total number of results
    Basic usage::
        object = paginate(select([User]), session, 1, 10, "asc", "email")
    """
    total_results = await session.scalar(
        select(func.count()).select_from(query.subquery())
    )
    query = _sort_by(query, direction, sort_by)

    query = _limit(query, page_size)

    # Page size defaults to total results
    if page_size is None or (page_size > total_results and total_results > 0):
        page_size = total_results

    query = _offset(query, page_number, page_size)

    # Page number defaults to 1
    if page_number is None:
        page_number = 1
    if use_scalars:
        results = await session.scalars(query)
        results = results.all()
    else:
        results = await session.execute(query)
        results = results.mappings().all()
    if format_to_dict:
        if results and isinstance(results[0], RowMapping):
            results = [dict(k) for k in results]
        else:
            results = [dataclasses.asdict(k) for k in results]
    return {
        "items": results,
        "page": page_number,
        "size": page_size,
        "total": total_results,
    }


def _limit(query: Select, page_size: Optional[int]) -> Select:
    if page_size is not None:
        if page_size < 0:
            raise Exception("Page size should not be negative: {}".format(page_size))

        query = query.limit(page_size)

    return query


def _offset(
    query: Select, page_number: Optional[int], page_size: Optional[int]
) -> Select:
    if page_number is not None:
        if page_number < 1:
            raise Exception("Page number should be positive: {}".format(page_number))

        query = query.offset((page_number - 1) * page_size)

    return query


def __get_best_sort_column(columns):
    primary = next((c for c in columns if getattr(c, "primary_key", False)), None)
    if primary is not None:
        return primary

    unique = next((c for c in columns if getattr(c, "unique", False)), None)
    if unique is not None:
        return unique

    return None


def _sort_by(query: Select, direction: Optional[str], sort_by: Optional[str]) -> Select:
    """
    Sorts query by a specific column in ascending or descending order.
    If no sort_by is specified and query has no existing order_by clause,
    defaults to sorting by primary key/unique column if it exists.
    """
    # If query already has ordering, return as is
    if query._order_by_clauses:
        return query

    columns = inspect(query).selected_columns

    unique_column = __get_best_sort_column(columns)

    # If sort_by is specified, try to sort by that column
    if sort_by:
        for item in columns:
            if sort_by == item.key:
                query = query.order_by(desc(item) if direction == "desc" else asc(item))
                if not getattr(item, "unique", False) or not getattr(
                    item, "primary_key", False
                ):
                    if unique_column is not None:
                        query = query.order_by(unique_column)
                    else:
                        logger.warning(
                            "You selected a non-deterministic column for sorting. Pagination may yield duplicate results."
                        )
                return query

    # If no sort_by and no existing order_by, try to sort by unique column
    if unique_column is not None:
        return query.order_by(unique_column)
    logger.warning(
        "You are using pagination without a unique column. Pagination may yield inconsistent results."
    )
    return query
