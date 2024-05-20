from typing import Optional
from sqlalchemy import select, func, desc, Select, inspect, asc
from sqlalchemy.orm import Session


def paginate(
    query: Select,
    session: Session,
    recurse: bool = True,
    page_number: int = None,
    page_size: int = None,
    direction: str = None,
    sort_by: str = None,
):
    """Apply pagination to a SQLAlchemy query object.
    :param query:
        SQLAlchemy Select object.
    :param session:
        SQLAlchemy Session object.
    :param page_number:
        Page to be returned (starts and defaults to 1).
    :param page_size:
        Maximum number of results to be returned in the page (defaults
        to the total results).
    :param direction:
        Direction of ordering, asc or desc
    :param sort_by:
        Column for sorting
    :returns:
        A dict with items (SQLAlchemy objects converted to dict),
        page number, desired page size, total number of results
    Basic usage::
        object = paginate(select([User]), session, 1, 10, "asc", "email")
    """
    total_results = session.scalar(select(func.count()).select_from(query.subquery()))

    query = _sort_by(query, direction, sort_by)

    query = _limit(query, page_size)

    # cast to int if params are str
    if isinstance(page_number, str):
        page_number = int(page_number)
    if isinstance(page_size, str):
        page_size = int(page_size)

    # Page size defaults to total results
    if page_size is None or (page_size > total_results and total_results > 0):
        page_size = total_results

    query = _offset(query, page_number, page_size)

    # Page number defaults to 1
    if page_number is None:
        page_number = 1

    results = session.scalars(query).all()

    return {
        "items": [k.to_dict(recurse=recurse) for k in results],
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


def _sort_by(query: Select, direction: Optional[str], sort_by: Optional[str]) -> Select:
    """
    Sorts query by a specific column in ascending or descending order,
    after verifying that the column exists.
    """
    if sort_by:
        columns = [column.key for column in inspect(query).selected_columns]
        if sort_by not in columns:
            sort_by = None

    if sort_by and direction == "desc":
        query = query.order_by(desc(sort_by))
    elif sort_by and direction == "asc":
        query = query.order_by(asc(sort_by))

    return query
