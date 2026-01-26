import pytest
import mongomock
from mongoengine import (
    Document,
    StringField,
    IntField,
    connect,
    disconnect,
    get_connection,
)
from mrkutil.pagination.mongoengine import paginate


class UserDoc(Document):
    name = StringField()
    age = IntField()

    def to_dict(self):
        return {"name": self.name, "age": self.age}


@pytest.fixture(autouse=True)
def setup_db():
    connect(
        "mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
        alias="default",
        uuidRepresentation="standard",
    )
    conn = get_connection()
    yield conn
    disconnect(alias="default")


@pytest.fixture
def sample_data():
    UserDoc.drop_collection()
    docs = [UserDoc(name=f"User{i}", age=20 + i).save() for i in range(20)]
    return docs


def test_basic_pagination(sample_data):
    query = UserDoc.objects
    result = paginate(query, page_number=1, page_size=5)

    assert len(result["items"]) == 5
    assert result["page"] == 1
    assert result["size"] == 5
    assert result["total"] == 20


def test_pagination_with_sorting(sample_data):
    query = UserDoc.objects
    result = paginate(
        query, page_number=1, page_size=5, direction="desc", sort_by="name"
    )

    assert len(result["items"]) == 5
    assert result["items"][0]["name"] == "User9"


def test_pagination_defaults(sample_data):
    query = UserDoc.objects
    result = paginate(query)

    assert len(result["items"]) == 20
    assert result["page"] == 1
    assert result["size"] == 20


def test_pagination_string_params(sample_data):
    query = UserDoc.objects
    result = paginate(query, page_number="2", page_size="5")

    assert len(result["items"]) == 5
    assert result["page"] == 2
    assert result["size"] == 5


def test_pagination_random_sort(sample_data):
    query = UserDoc.objects
    result1 = paginate(query, direction="rand", page_size=20)
    result2 = paginate(query, direction="rand", page_size=20)

    # Due to random sorting, results should likely be different
    assert result1["items"] != result2["items"]


def test_pagination_out_of_bounds(sample_data):
    query = UserDoc.objects
    result = paginate(query, page_number=100, page_size=10)

    assert len(result["items"]) == 0
    assert result["page"] == 100
    assert result["size"] == 10
    assert result["total"] == 20
