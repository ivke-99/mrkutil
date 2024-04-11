def paginate(
    query,
    page_number: int = None,
    page_size: int = None,
    direction: str = None,
    sort_by: str = None,
):
    """Apply pagination to a SQLAlchemy query object.
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
        A dict with items(sqlalchemy objects converted to dict),
        page number, desired page size, total number of results
    Basic usage::
        object = paginate(query, 1, 10, "asc", "email")
    """
    total_results = query.count()

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

    return {
        "items": [k._asdict() for k in query.all()],
        "page": page_number,
        "size": page_size,
        "total": total_results,
    }


def _limit(query, page_size):
    if page_size is not None:
        if page_size < 0:
            raise Exception("Page size should not be negative: {}".format(page_size))

        query = query.limit(page_size)

    return query


def _offset(query, page_number, page_size):
    if page_number is not None:
        if page_number < 1:
            raise Exception("Page number should be positive: {}".format(page_number))

        query = query.offset((page_number - 1) * page_size)

    return query


def _sort_by(query, direction, sort_by):
    """
    If None is passed to sqlalchemy order_by, it will do default sorting
    This way we are allowing sorting by ascending/descending without a specified
    sort by parameter
    """
    # check if sort by exists in columns otherwise default it to None
    if sort_by not in query.statement.columns.keys():
        sort_by = None
    if direction == "desc":
        from sqlalchemy import desc

        query = query.order_by(desc(sort_by))
    else:
        query = query.order_by(sort_by)
    return query
