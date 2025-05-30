import logging

logger = logging.getLogger(__name__)


def pagination_params(
    page: int | None = None,
    size: int = 10,
    direction: str | None = "asc",
    sort_by: str | None = None,
):
    """
    Generate pagination parameters.
    Commonly used in dependency injection.

    Args:
        page (int | None): The page number. Defaults to None.
        size (int): The number of items per page. Defaults to 10.
        direction (str | None): The sorting direction. Defaults to "asc".
        sort_by (str | None): The field to sort by. Defaults to None.

    Returns:
        dict: A dictionary containing the pagination parameters.

    """
    if not page or page <= 0:
        logger.warning("Page is less than or equal to 0, setting to 1")
        page = 1
    if size <= 0:
        logger.warning("Size is less than or equal to 0, setting to 10")
        size = 10
    if size > 100:
        logger.warning("Size is greater than 100, setting to 100")
        size = 100
    return {"page": page, "size": size, "direction": direction, "sort_by": sort_by}
