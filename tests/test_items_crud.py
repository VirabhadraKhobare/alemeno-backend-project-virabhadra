import os

from app import create_app


def test_items_crud():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    client = app.test_client()

    # initially empty
    res = client.get("/api/v1/items/")
    assert res.status_code == 200
    assert res.get_json() == []

    # create with missing name -> 400
    res = client.post("/api/v1/items/", json={"description": "no name"})
    assert res.status_code == 400

    # create valid
    res = client.post(
        "/api/v1/items/",
        json={"name": "Item A", "description": "desc A"},
    )
    assert res.status_code == 201
    item = res.get_json()
    assert item["name"] == "Item A"
    item_id = item["id"]

    # get by id
    res = client.get(f"/api/v1/items/{item_id}")
    assert res.status_code == 200
    got = res.get_json()
    assert got["id"] == item_id

    # list contains the item
    res = client.get("/api/v1/items/")
    assert res.status_code == 200
    items = res.get_json()
    assert any(i["id"] == item_id for i in items)

    # delete
    res = client.delete(f"/api/v1/items/{item_id}")
    assert res.status_code == 200
    assert res.get_json()["deleted"] == item_id

    # get after delete -> 404
    res = client.get(f"/api/v1/items/{item_id}")
    assert res.status_code == 404
