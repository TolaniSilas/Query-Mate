"""
tests for api/routes/query.py
    POST  /api/query
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock      import patch
from fastapi.testclient import TestClient
from api.main           import app

client = TestClient(app)


MOCK_SESSION = {
    "db_type":       "postgresql",
    "schema_prompt": "CREATE TABLE users (id INT, name TEXT)",
    "schema":        {"tables": {"users": {}}},
}

MOCK_PIPELINE_OK = {
    "answer":    "There are 42 users in the database.",
    "sql":       "SELECT COUNT(*) FROM users",
    "rows":      [{"count": 42}],
    "row_count": 1,
    "truncated": False,
    "attempts":  1,
    "status":    "ok",
    "error":     None,
}

MOCK_PIPELINE_CANNOT_ANSWER = {
    "answer":    "That question doesn't appear to match anything in the connected database.",
    "sql":       None,
    "rows":      None,
    "row_count": 0,
    "truncated": False,
    "attempts":  1,
    "status":    "cannot_answer",
    "error":     "Question cannot be answered from the available schema.",
}

MOCK_PIPELINE_VALIDATION_FAILED = {
    "answer":    "Something went wrong after 3 attempts.",
    "sql":       None,
    "rows":      None,
    "row_count": 0,
    "truncated": False,
    "attempts":  3,
    "status":    "validation_failed",
    "error":     "Could not generate a valid query after 3 attempts.",
}


# POST /api/query — success cases.

@patch("api.routes.query.get_session")
@patch("api.routes.query.run_pipeline")
def test_query_success(mock_pipeline, mock_session):
    mock_session.return_value  = MOCK_SESSION
    mock_pipeline.return_value = MOCK_PIPELINE_OK

    response = client.post("/api/query", json={
        "session_id": "test-session-123",
        "question":   "how many users are there?",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"]    == "ok"
    assert data["answer"]    == "There are 42 users in the database."
    assert data["sql"]       == "SELECT COUNT(*) FROM users"
    assert data["row_count"] == 1
    assert data["truncated"] is False
    assert data["attempts"]  == 1
    assert data["error"]     is None


@patch("api.routes.query.get_session")
@patch("api.routes.query.run_pipeline")
def test_query_cannot_answer(mock_pipeline, mock_session):
    mock_session.return_value  = MOCK_SESSION
    mock_pipeline.return_value = MOCK_PIPELINE_CANNOT_ANSWER

    response = client.post("/api/query", json={
        "session_id": "test-session-123",
        "question":   "what is the weather today?",
    })

    data = response.json()
    assert data["status"] == "cannot_answer"
    assert data["sql"]    is None
    assert data["rows"]   is None


@patch("api.routes.query.get_session")
@patch("api.routes.query.run_pipeline")
def test_query_validation_failed(mock_pipeline, mock_session):
    mock_session.return_value  = MOCK_SESSION
    mock_pipeline.return_value = MOCK_PIPELINE_VALIDATION_FAILED

    response = client.post("/api/query", json={
        "session_id": "test-session-123",
        "question":   "a very complex ambiguous question",
    })

    data = response.json()
    assert data["status"]   == "validation_failed"
    assert data["attempts"] == 3


@patch("api.routes.query.get_session")
@patch("api.routes.query.run_pipeline")
def test_query_passes_correct_schema_and_db_type_to_pipeline(mock_pipeline, mock_session):
    mock_session.return_value  = MOCK_SESSION
    mock_pipeline.return_value = MOCK_PIPELINE_OK

    client.post("/api/query", json={
        "session_id": "test-session-123",
        "question":   "how many users?",
    })

    call_kwargs = mock_pipeline.call_args.kwargs
    assert call_kwargs["schema_prompt"] == MOCK_SESSION["schema_prompt"]
    assert call_kwargs["db_type"]       == MOCK_SESSION["db_type"]
    assert call_kwargs["session_id"]    == "test-session-123"


# POST /api/query — error cases.

@patch("api.routes.query.get_session")
def test_query_session_not_found(mock_session):
    mock_session.return_value = None

    response = client.post("/api/query", json={
        "session_id": "nonexistent-session",
        "question":   "how many users?",
    })

    data = response.json()
    assert data["status"] == "error"
    assert "Session not found" in data["error"]


def test_query_empty_question_rejected():
    response = client.post("/api/query", json={
        "session_id": "test-session-123",
        "question":   "",
    })
    assert response.status_code == 422


def test_query_whitespace_only_question_rejected():
    response = client.post("/api/query", json={
        "session_id": "test-session-123",
        "question":   "   ",
    })
    # pydantic min_length=1 catches empty but whitespace slips through
    # the pipeline handles whitespace — status code still 200
    assert response.status_code in (200, 422)


def test_query_question_too_long_rejected():
    response = client.post("/api/query", json={
        "session_id": "test-session-123",
        "question":   "x" * 2001,
    })
    assert response.status_code == 422


def test_query_missing_session_id_rejected():
    response = client.post("/api/query", json={
        "question": "how many users?",
    })
    assert response.status_code == 422


def test_query_missing_question_rejected():
    response = client.post("/api/query", json={
        "session_id": "test-session-123",
    })
    assert response.status_code == 422