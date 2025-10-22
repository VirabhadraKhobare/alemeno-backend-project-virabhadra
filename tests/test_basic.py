import os
from app import create_app


def test_health():
    app = create_app()
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"


def test_create_and_list_items():
    # use temp sqlite
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    client = app.test_client()

    # create
    res = client.post(
        "/api/v1/items/", json={"name": "Test Item", "description": "desc"}
    )
    assert res.status_code == 201
    item = res.get_json()
    assert item["name"] == "Test Item"

    # list
    res = client.get("/api/v1/items/")
    assert res.status_code == 200
    items = res.get_json()
    assert any(i["name"] == "Test Item" for i in items)
