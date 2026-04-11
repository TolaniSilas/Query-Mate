"""
tests for api/routes/schema.py
    GET  /api/schema?session_id=xxx
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock      import patch
from fastapi.testclient import TestClient
from serving.main       import app

client = TestClient(app)


MOCK_SESSION = {
    "db_type":       "postgresql",
    "schema_prompt": "CREATE TABLE users (id INT)\nCREATE TABLE orders (id INT, user_id INT)",
    "schema":        {
        "tables": {
            "users":  {"columns": [{"name": "id", "type": "INT"}]},
            "orders": {"columns": [{"name": "id", "type": "INT"}, {"name": "user_id", "type": "INT"}]},
        }
    },
}


# GET /api/schema — success cases.
@patch("serving.routes.schema.get_session")
def test_get_schema_success(mock_session):
    mock_session.return_value = MOCK_SESSION

    response = client.get("/api/schema?session_id=test-session-123")

    assert response.status_code == 200
    data = response.json()
    assert data["status"]  == "ok"
    assert data["db_type"] == "postgresql"
    assert data["tables"]  is not None
    assert data["prompt"]  is not None
    assert data["error"]   is None


@patch("serving.routes.schema.get_session")
def test_get_schema_returns_correct_tables(mock_session):
    mock_session.return_value = MOCK_SESSION

    response = client.get("/api/schema?session_id=test-session-123")

    data   = response.json()
    tables = data["tables"]
    assert "users"  in tables
    assert "orders" in tables


@patch("serving.routes.schema.get_session")
def test_get_schema_returns_prompt_string(mock_session):
    mock_session.return_value = MOCK_SESSION

    response = client.get("/api/schema?session_id=test-session-123")

    data = response.json()
    assert "CREATE TABLE" in data["prompt"]


@patch("serving.routes.schema.get_session")
def test_get_schema_returns_correct_db_type(mock_session):
    mock_session.return_value = {**MOCK_SESSION, "db_type": "mysql"}

    response = client.get("/api/schema?session_id=test-session-123")

    assert response.json()["db_type"] == "mysql"


# GET /api/schema — error cases.
@patch("serving.routes.schema.get_session")
def test_get_schema_session_not_found(mock_session):
    mock_session.return_value = None

    response = client.get("/api/schema?session_id=nonexistent-session")

    data = response.json()
    assert data["status"] == "error"
    assert data["tables"] is None
    assert data["prompt"] is None
    assert "Session not found" in data["error"]


def test_get_schema_missing_session_id_rejected():
    response = client.get("/api/schema")
    # FastAPI requires the query param — returns 422
    assert response.status_code == 422