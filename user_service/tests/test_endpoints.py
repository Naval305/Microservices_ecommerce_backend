def test_unknown_route_returns_404(client):
    response = client.get("/unknown-route")

    assert response.status_code == 404
    assert response.get_json()["code"] == "not_found"


def test_wrong_method_returns_405(client):
    response = client.get("/api/users/login")

    assert response.status_code == 405
    assert response.get_json()["code"] == "method_not_allowed"


def test_missing_login_email_returns_validation_error(client):
    response = client.post("/api/users/login", json={"password": "abc"})
    body = response.get_json()

    assert response.status_code == 422
    assert body["code"] == "validation_error"
    assert "errors" in body


def test_registration_with_unknown_field_returns_validation_error(client):
    payload = {
        "first_name": "Naval",
        "last_name": "Shankhdhar",
        "email": "naval@example.com",
        "password": "naval@123456",
        "unexpected": "field",
    }

    response = client.post("/api/users/registration", json=payload)
    body = response.get_json()

    assert response.status_code == 422
    assert body["code"] == "validation_error"
    assert "errors" in body


def test_duplicate_email_returns_409(client):
    payload = {
        "first_name": "Naval",
        "last_name": "Shankhdhar",
        "email": "naval@example.com",
        "password": "naval@123456",
    }

    first_response = client.post("/api/users/registration", json=payload)
    second_response = client.post("/api/users/registration", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.get_json()["code"] == "email_already_exists"


def test_unexpected_error_returns_500_without_internal_detail(client):
    response = client.get("/raise-unexpected-error")
    body = response.get_json()

    assert response.status_code == 500
    assert body["code"] == "internal_server_error"
    assert "sensitive internal detail" not in str(body)


def test_refresh_token_200(client, auth_tokens):
    response = client.post(
        "/api/users/refresh",
        headers={"Authorization": f"Bearer {auth_tokens['refresh_token']}"},
    )
    print(response.get_json())
    assert response.status_code == 200
    assert response.get_json()["message"] == "Success"


def test_refresh_token_with_invalid_token_returns_401(client):
    response = client.post("/api/users/refresh", headers={"Authorization": "Bearer invalidtoken"})
    body = response.get_json()
    assert response.status_code == 401
    assert body["code"] == "invalid_refresh_token"
