import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.main import create_app, db


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "PROPAGATE_EXCEPTIONS": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    @app.get("/raise-unexpected-error")
    def raise_unexpected_error():
        raise RuntimeError("sensitive internal detail")

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def test_user(client):
    user = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "testpassword123",
    }

    response = client.post(
        "/api/users/registration",
        json=user,
    )

    assert response.status_code == 201, response.get_json()

    # user_id = response.get_json()["data"]["user_id"]

    return user


@pytest.fixture()
def auth_tokens(client, test_user):
    response = client.post(
        "/api/users/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )

    assert response.status_code == 200

    return response.get_json()["data"]
