from bson import ObjectId
from fastapi.testclient import TestClient


def test_category_crud_flow(client: TestClient) -> None:
    created = client.post("/api/v1/category/create", json={"name": "Electronics"})

    assert created.status_code == 200
    assert created.json()["success"] is True
    category = created.json()["data"]
    assert category["name"] == "Electronics"
    assert category["ancestors"] == []

    listed = client.get("/api/v1/category/list")
    assert listed.status_code == 200
    assert listed.json()["data"] == [category]

    updated = client.patch(
        f"/api/v1/category/update/{category['_id']}", json={"name": "Computers"}
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "Computers"

    deleted = client.delete(f"/api/v1/category/delete/{category['_id']}")
    assert deleted.status_code == 200
    assert deleted.json() == {
        "success": True,
        "message": "Category deleted successfully",
        "data": {"deleted_count": 1},
    }


def test_category_create_rejects_duplicate_and_missing_parent(client: TestClient) -> None:
    assert client.post("/api/v1/category/create", json={"name": "Books"}).status_code == 200

    duplicate = client.post("/api/v1/category/create", json={"name": "Books"})
    assert duplicate.status_code == 409
    assert duplicate.json()["message"] == "Category already exists"

    missing_parent = client.post(
        "/api/v1/category/create",
        json={"name": "Fiction", "parent_id": str(ObjectId())},
    )
    assert missing_parent.status_code == 404
    assert missing_parent.json()["message"] == "Parent category does not exist"


def test_category_update_rejects_missing_category_and_self_parent(client: TestClient) -> None:
    missing = client.patch(
        f"/api/v1/category/update/{ObjectId()}", json={"name": "Missing"}
    )
    assert missing.status_code == 409
    assert missing.json()["message"] == "Category does not exists"

    category = client.post("/api/v1/category/create", json={"name": "Clothing"}).json()[
        "data"
    ]
    self_parent = client.patch(
        f"/api/v1/category/update/{category['_id']}",
        json={"parent_id": category["_id"]},
    )
    assert self_parent.status_code == 409
    assert self_parent.json()["message"] == "A category cannot be its own parent"


def test_category_request_validation_error(client: TestClient) -> None:
    response = client.post("/api/v1/category/create", json={"name": ""})

    assert response.status_code == 422
    assert response.json()["detail"]
