import pytest
from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from src import crud
from src.api.schemas.item import ItemResponse
from src.models import Item
from src.tests.factories.item_factory import ItemFactory

BASE_URL = "api/items"


def test_create_item(client):
    resp = client.post(
        BASE_URL, json={"title": "test title", "description": "test description"}
    )
    assert resp.status_code == 201


def test_get_items(client):
    # create some items
    item_1 = ItemFactory(title="test title 1", description="test description 1")
    item_2 = ItemFactory(title="test title 2", description="test description 2")

    resp = client.get(BASE_URL)
    assert resp.status_code == 200

    assert resp.json() == [
        ItemResponse(**item_1.model_dump()).model_dump(mode="json"),
        ItemResponse(**item_2.model_dump()).model_dump(mode="json"),
    ]


def test_get_item(client):
    # create some items
    _ = ItemFactory(title="test title 1", description="test description 1")
    item_2 = ItemFactory(title="test title 2", description="test description 2")

    resp = client.get(f"{BASE_URL}/{str(item_2.id)}")

    assert resp.status_code == 200
    # snake_case to camelCase!
    assert resp.json()["isActive"]
    assert resp.json() == ItemResponse(**item_2.model_dump()).model_dump(mode="json")


def test_update_item(client):
    item = ItemFactory(title="test title 1", description="test description 1")
    update_data = {"title": "New title"}
    resp = client.patch(f"{BASE_URL}/{str(item.id)}", json=update_data)

    assert resp.status_code == 200
    expected = ItemResponse(**item.model_dump()).model_dump(mode="json")
    expected["title"] = update_data["title"]
    assert resp.json() == expected


def test_delete_item(client, db):
    item = ItemFactory(title="test title 1", description="test description 1")
    item_id = item.id
    resp = client.delete(f"{BASE_URL}/{str(item.id)}")

    assert resp.status_code == 204

    with pytest.raises(NoResultFound):
        crud.item.get(db=db, id=item_id)
