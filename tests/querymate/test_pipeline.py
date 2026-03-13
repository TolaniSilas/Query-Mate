"""
tests for core/pipeline.py — the main orchestrator.
uses mocks so no real DB or LLM calls are made.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import patch, MagicMock
from querymate.core.pipeline import run_pipeline


MOCK_SESSION = {
    "db_type": "postgresql",
    "schema_prompt": "CREATE TABLE users (id INT, name TEXT)",
}

MOCK_SQL_RESULT_OK = {
    "sql": "SELECT * FROM users LIMIT 10",
    "rows": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
    "status": "ok",
    "attempts": 1,
    "error": None,
}

MOCK_SQL_RESULT_CANNOT_ANSWER = {
    "sql": None,
    "rows": None,
    "status": "cannot_answer",
    "attempts": 1,
    "error": "Question cannot be answered from the available schema.",
}


@patch("querymate.core.pipeline.get_session")
@patch("querymate.core.pipeline.run_sql_agent")
@patch("querymate.core.pipeline.generate_response")
def test_pipeline_ok(mock_response, mock_sql_agent, mock_get_session):
    mock_get_session.return_value = MOCK_SESSION
    mock_sql_agent.return_value = MOCK_SQL_RESULT_OK
    mock_response.return_value = {
        "answer": "There are 2 users.",
        "row_count": 2,
        "truncated": False,
        "status": "ok",
    }

    result = run_pipeline(
        question = "how many users are there?",
        schema_prompt = MOCK_SESSION["schema_prompt"],
        db_type = "postgresql",
        session_id = "test-session",
    )

    assert result["status"] == "ok"
    assert result["answer"] == "There are 2 users."
    assert result["sql"] == MOCK_SQL_RESULT_OK["sql"]
    assert result["row_count"] == 2
    assert result["error"] is None


@patch("querymate.core.pipeline.get_session")
@patch("querymate.core.pipeline.run_sql_agent")
@patch("querymate.core.pipeline.generate_response")
def test_pipeline_cannot_answer(mock_response, mock_sql_agent, mock_get_session):
    mock_get_session.return_value = MOCK_SESSION
    mock_sql_agent.return_value = MOCK_SQL_RESULT_CANNOT_ANSWER
    mock_response.return_value = {
        "answer": "That question doesn't appear to match anything in the connected database.",
        "row_count": 0,
        "truncated": False,
        "status": "cannot_answer",
    }

    result = run_pipeline(
        question = "what is the meaning of life?",
        schema_prompt = MOCK_SESSION["schema_prompt"],
        db_type = "postgresql",
        session_id = "test-session",
    )

    assert result["status"] == "cannot_answer"
    assert result["sql"] is None
    assert result["rows"] is None


@patch("querymate.core.pipeline.get_session")
@patch("querymate.core.pipeline.run_sql_agent")
@patch("querymate.core.pipeline.generate_response")
def test_pipeline_security_rejected(mock_response, mock_sql_agent, mock_get_session):
    mock_get_session.return_value = MOCK_SESSION
    mock_sql_agent.return_value   = {
        "sql": "DELETE FROM users",
        "rows": None,
        "status": "ok",
        "attempts": 1,
        "error": "SECURITY_REJECTED: Forbidden keyword detected: 'DELETE'.",
    }
    mock_response.return_value = {
        "answer": "Something went wrong.",
        "row_count": 0,
        "truncated": False,
        "status": "security_rejected",
    }

    result = run_pipeline(
        question = "delete all users",
        schema_prompt = MOCK_SESSION["schema_prompt"],
        db_type = "postgresql",
        session_id = "test-session",
    )

    assert result["status"] == "security_rejected"