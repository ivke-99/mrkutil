def paginate_mongo(
    query,
    page_number: int = None,
    page_size: int = None,
    direction: str = None,
    sort_by: str = None
):
    total_results = query.count()

    query = _sort_by(query, direction, sort_by)

    # cast to int if params are str
    if isinstance(page_number, str):
        page_number = int(page_number)
    if isinstance(page_size, str):
        page_size = int(page_size)

    if page_size is None or (page_size > total_results and total_results > 0):
        page_size = total_results

    if page_number is None:
        page_number = 1

    from_pag = (page_number - 1) * page_size
    to_pag = (page_number - 1) * page_size + page_size

    return {
        "items": [k.to_dict() for k in query[from_pag:to_pag].all()],
        "page": page_number,
        "size": page_size,
        "total": total_results
    }


def _sort_by(query, direction, sort_by):
    sort = "+"
    if direction == "desc":
        sort = "-"
    if not sort_by:
        sort_by = "_id"
    sort += sort_by
    return query.order_by(sort)
