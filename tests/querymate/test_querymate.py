"""
tests for querymate/__init__.py — the public QueryMate class.
uses mocks so no real DB or LLM calls are made.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import patch, MagicMock
from querymate import QueryMate, QueryResult


MOCK_CONNECT_OK = {
    "status":      "ok",
    "db_type":     "postgresql",
    "table_count": 3,
    "tables":      ["users", "orders", "products"],
    "error":       None,
}

MOCK_SESSION = {
    "db_type":       "postgresql",
    "schema_prompt": "CREATE TABLE users (id INT, name TEXT)",
    "schema":        {"tables": {}},
}

MOCK_PIPELINE_RESULT = {
    "answer":    "There are 42 users in the database.",
    "sql":       "SELECT COUNT(*) FROM users",
    "rows":      [{"count": 42}],
    "row_count": 1,
    "truncated": False,
    "attempts":  1,
    "status":    "ok",
    "error":     None,
}


@patch("querymate.connect")
def test_querymate_connects_successfully(mock_connect):
    mock_connect.return_value = MOCK_CONNECT_OK

    qm = QueryMate(
        db_type      = "postgresql",
        database_url = "postgresql://user:pass@host/db",
    )

    assert qm.db_type     == "postgresql"
    assert qm.table_count == 3
    assert qm.tables      == ["users", "orders", "products"]
    assert qm._connected  is True


@patch("querymate.connect")
def test_querymate_raises_on_connection_failure(mock_connect):
    mock_connect.return_value = {
        "status": "error",
        "error":  "could not connect to server",
    }

    with pytest.raises(ConnectionError, match="could not connect to server"):
        QueryMate(db_type="postgresql", database_url="postgresql://bad/url")


@patch("querymate.connect")
@patch("querymate.get_session")
@patch("querymate.run_pipeline")
def test_ask_returns_query_result(mock_pipeline, mock_session, mock_connect):
    mock_connect.return_value  = MOCK_CONNECT_OK
    mock_session.return_value  = MOCK_SESSION
    mock_pipeline.return_value = MOCK_PIPELINE_RESULT

    qm     = QueryMate(db_type="postgresql", database_url="postgresql://user:pass@host/db")
    result = qm.ask("how many users are there?")

    assert isinstance(result, QueryResult)
    assert result.status    == "ok"
    assert result.answer    == "There are 42 users in the database."
    assert result.sql       == "SELECT COUNT(*) FROM users"
    assert result.row_count == 1
    assert result.error     is None


@patch("querymate.connect")
def test_ask_raises_on_empty_question(mock_connect):
    mock_connect.return_value = MOCK_CONNECT_OK

    qm = QueryMate(db_type="postgresql", database_url="postgresql://user:pass@host/db")

    with pytest.raises(ValueError, match="question cannot be empty"):
        qm.ask("   ")


@patch("querymate.connect")
@patch("querymate.disconnect")
def test_disconnect_sets_connected_false(mock_disconnect, mock_connect):
    mock_connect.return_value    = MOCK_CONNECT_OK
    mock_disconnect.return_value = {"status": "ok"}

    qm = QueryMate(db_type="postgresql", database_url="postgresql://user:pass@host/db")
    qm.disconnect()

    assert qm._connected is False


@patch("querymate.connect")
def test_ask_after_disconnect_raises(mock_connect):
    mock_connect.return_value = MOCK_CONNECT_OK

    qm = QueryMate(db_type="postgresql", database_url="postgresql://user:pass@host/db")
    qm._connected = False

    with pytest.raises(RuntimeError, match="not connected"):
        qm.ask("how many users?")


@patch("querymate.connect")
def test_sqlite_requires_sqlite_path(mock_connect):
    with pytest.raises(ValueError, match="sqlite_path is required"):
        QueryMate(db_type="sqlite")


@patch("querymate.connect")
def test_postgresql_requires_database_url(mock_connect):
    with pytest.raises(ValueError, match="database_url is required"):
        QueryMate(db_type="postgresql")


@patch("querymate.connect")
@patch("querymate.disconnect")
def test_context_manager_disconnects(mock_disconnect, mock_connect):
    mock_connect.return_value    = MOCK_CONNECT_OK
    mock_disconnect.return_value = {"status": "ok"}

    with QueryMate(db_type="postgresql", database_url="postgresql://user:pass@host/db") as qm:
        assert qm._connected is True

    assert qm._connected is False