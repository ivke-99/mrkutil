def pagination_params(
    page: int | None = None,
    size: int = 10,
    direction: str | None = "asc",
    sort_by: str | None = None
):
    if not page or page <= 0:
        page = 1
    if size <= 0:
        size = 10
    if size > 100:
        size = 100
    return {
        "page": page,
        "size": size,
        "direction": direction,
        "sort_by": sort_by
    }