"""
tests for api/routes/connection.py
    POST   /api/connect
    DELETE /api/disconnect
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock      import patch
from fastapi.testclient import TestClient
from api.main           import app

client = TestClient(app)


MOCK_CONNECT_OK = {
    "status":      "ok",
    "db_type":     "postgresql",
    "table_count": 3,
    "tables":      ["users", "orders", "products"],
    "error":       None,
}


# POST /api/connect — success cases.

@patch("api.routes.connection.connect")
def test_connect_postgresql_success(mock_connect):
    mock_connect.return_value = MOCK_CONNECT_OK

    response = client.post("/api/connect", json={
        "db_type":      "postgresql",
        "database_url": "postgresql://user:pass@host/db",
    })

    assert response.status_code      == 200
    data = response.json()
    assert data["status"]            == "ok"
    assert data["session_id"]        is not None
    assert data["db_type"]           == "postgresql"
    assert data["table_count"]       == 3
    assert data["tables"]            == ["users", "orders", "products"]
    assert data["error"]             is None


@patch("api.routes.connection.connect")
def test_connect_mysql_success(mock_connect):
    mock_connect.return_value = {**MOCK_CONNECT_OK, "db_type": "mysql"}

    response = client.post("/api/connect", json={
        "db_type":      "mysql",
        "database_url": "mysql+pymysql://user:pass@host/db",
    })

    data = response.json()
    assert data["status"]  == "ok"
    assert data["db_type"] == "mysql"


@patch("api.routes.connection.connect")
def test_connect_sqlite_success(mock_connect):
    mock_connect.return_value = {**MOCK_CONNECT_OK, "db_type": "sqlite"}

    response = client.post("/api/connect", json={
        "db_type":    "sqlite",
        "sqlite_path": "/tmp/test.db",
    })

    data = response.json()
    assert data["status"]  == "ok"
    assert data["db_type"] == "sqlite"


# POST /api/connect — validation errors.

def test_connect_unsupported_db_type():
    response = client.post("/api/connect", json={
        "db_type":      "oracle",
        "database_url": "oracle://something",
    })

    data = response.json()
    assert data["status"]     == "error"
    assert data["session_id"] is None
    assert "Unsupported" in data["error"]


def test_connect_postgresql_missing_database_url():
    response = client.post("/api/connect", json={
        "db_type": "postgresql",
    })

    data = response.json()
    assert data["status"] == "error"
    assert "database_url" in data["error"]


def test_connect_sqlite_missing_sqlite_path():
    response = client.post("/api/connect", json={
        "db_type": "sqlite",
    })

    data = response.json()
    assert data["status"] == "error"
    assert "sqlite_path" in data["error"]


@patch("api.routes.connection.connect")
def test_connect_db_error_propagated(mock_connect):
    mock_connect.return_value = {"status": "error", "error": "could not connect to server"}

    response = client.post("/api/connect", json={
        "db_type":      "postgresql",
        "database_url": "postgresql://bad/url",
    })

    data = response.json()
    assert data["status"]     == "error"
    assert data["session_id"] is None
    assert "could not connect" in data["error"]


@patch("api.routes.connection.connect")
def test_connect_session_id_is_unique_per_request(mock_connect):
    mock_connect.return_value = MOCK_CONNECT_OK

    response_1 = client.post("/api/connect", json={
        "db_type": "postgresql", "database_url": "postgresql://user:pass@host/db"
    })
    response_2 = client.post("/api/connect", json={
        "db_type": "postgresql", "database_url": "postgresql://user:pass@host/db"
    })

    session_1 = response_1.json()["session_id"]
    session_2 = response_2.json()["session_id"]
    assert session_1 != session_2


# DELETE /api/disconnect.

@patch("api.routes.connection.disconnect")
def test_disconnect_success(mock_disconnect):
    mock_disconnect.return_value = {"status": "ok", "error": None}

    response = client.delete("/api/disconnect?session_id=test-session-123")

    assert response.status_code       == 200
    assert response.json()["status"]  == "ok"
    assert response.json()["error"]   is None


@patch("api.routes.connection.disconnect")
def test_disconnect_session_not_found(mock_disconnect):
    mock_disconnect.return_value = {"status": "error", "error": "Session not found."}

    response = client.delete("/api/disconnect?session_id=nonexistent")

    data = response.json()
    assert data["status"] == "error"
    assert "Session not found" in data["error"]