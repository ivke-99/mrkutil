from mrkutil.pagination import pagination_params


def test_pagination_params_defaults():
    result = pagination_params()
    assert result == {"page": 1, "size": 10, "direction": "asc", "sort_by": None}


def test_pagination_params_custom():
    result = pagination_params(page=2, size=20, direction="desc", sort_by="name")
    assert result == {"page": 2, "size": 20, "direction": "desc", "sort_by": "name"}


def test_pagination_params_invalid_page():
    result = pagination_params(page=0)
    assert result["page"] == 1

    result = pagination_params(page=-1)
    assert result["page"] == 1


def test_pagination_params_invalid_size():
    result = pagination_params(size=0)
    assert result["size"] == 10

    result = pagination_params(size=-10)
    assert result["size"] == 10

    result = pagination_params(size=200)
    assert result["size"] == 100


def test_pagination_params_none_page():
    result = pagination_params(page=None)
    assert result["page"] == 1
