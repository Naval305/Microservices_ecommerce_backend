from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError

from app.db.session import get_client
from app.main import app


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/v1/server/healthz")

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "OK", "data": None}


def test_ready_check_when_database_is_available(client: TestClient) -> None:
    response = client.get("/api/v1/server/readyz")

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "OK", "data": None}


def test_ready_check_when_database_is_unavailable(client: TestClient) -> None:
    class UnavailableClient:
        class Admin:
            async def command(self, command: str) -> None:
                raise PyMongoError("database unavailable")

        admin = Admin()

    app.dependency_overrides[get_client] = lambda: UnavailableClient()
    response = client.get("/api/v1/server/readyz")

    assert response.status_code == 200
    assert response.json() == {"success": False, "message": "Not ready", "data": None}
