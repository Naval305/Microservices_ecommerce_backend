from bson import ObjectId
from fastapi.testclient import TestClient


def create_category(client: TestClient, name: str = "Electronics") -> str:
    response = client.post("/api/v1/category/create", json={"name": name})
    assert response.status_code == 200
    return response.json()["data"]["_id"]


def product_payload(category_id: str, **overrides: object) -> dict[str, object]:
    return {
        "name": "Wireless Mouse",
        "category_id": category_id,
        "price": "29.99",
        "quantity": 5,
        **overrides,
    }


def test_product_crud_flow_without_description(client: TestClient) -> None:
    category_id = create_category(client)
    created = client.post("/api/v1/products/create", json=product_payload(category_id))

    assert created.status_code == 200
    product = created.json()["data"]
    assert product["description"] is None
    assert product["normalized_name"] == "wireless mouse"
    assert product["category_id"] == category_id
    assert product["sku"].startswith(category_id[:3].upper())

    listed = client.get("/api/v1/products/list")
    assert listed.status_code == 200
    assert listed.json()["data"] == [product]

    updated = client.patch(
        f"/api/v1/products/update/{product['sku']}",
        json={"name": "Ergonomic Mouse", "price": "39.99"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "Ergonomic Mouse"
    assert updated.json()["data"]["normalized_name"] == "ergonomic mouse"
    assert updated.json()["data"]["price"] == 39.99

    deleted = client.delete(f"/api/v1/products/delete/{product['sku']}")
    assert deleted.status_code == 200
    assert deleted.json()["data"] == {"deleted_count": 1}


def test_product_create_rejects_duplicate_and_missing_category(client: TestClient) -> None:
    category_id = create_category(client)
    assert client.post("/api/v1/products/create", json=product_payload(category_id)).status_code == 200

    duplicate = client.post(
        "/api/v1/products/create", json=product_payload(category_id, name="  wireless   mouse  ")
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["message"] == "Product already exists"

    missing_category = client.post(
        "/api/v1/products/create", json=product_payload(str(ObjectId()))
    )
    assert missing_category.status_code == 409
    assert missing_category.json()["message"] == "Category does not exists"


def test_product_update_and_delete_reject_missing_product(client: TestClient) -> None:
    sku = "ABC-NOTFOUND"
    update = client.patch(f"/api/v1/products/update/{sku}", json={"quantity": 2})
    delete = client.delete(f"/api/v1/products/delete/{sku}")

    assert update.status_code == 409
    assert delete.status_code == 409
    assert update.json()["message"] == "Product does not exists"
    assert delete.json()["message"] == "Product does not exists"


def test_product_update_rejects_missing_category(client: TestClient) -> None:
    category_id = create_category(client)
    created = client.post("/api/v1/products/create", json=product_payload(category_id)).json()["data"]

    response = client.patch(
        f"/api/v1/products/update/{created['sku']}",
        json={"category_id": str(ObjectId())},
    )
    assert response.status_code == 409
    assert response.json()["message"] == "Category does not exists"


def test_product_request_validation_error(client: TestClient) -> None:
    response = client.post(
        "/api/v1/products/create",
        json=product_payload(str(ObjectId()), price="0"),
    )

    assert response.status_code == 422
    assert response.json()["detail"]
