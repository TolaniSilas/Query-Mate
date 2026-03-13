"""
tests for core/connection.py — database connection manager.
mocks sqlalchemy and schema inspector so no real DB calls are made.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from unittest.mock import patch, MagicMock
from querymate.core.connection import connect, disconnect, get_session, execute_query, _serialize


SESSION_ID = "test-session-abc"

MOCK_SCHEMA = {"tables": {"users": {}, "orders": {}}}
MOCK_SCHEMA_PROMPT = "CREATE TABLE users (id INT)"

MOCK_CONNECT_OK = {
    "status":      "ok",
    "db_type":     "postgresql",
    "table_count": 2,
    "tables":      ["users", "orders"],
    "error":       None,
}


def _mock_engine():
    engine      = MagicMock()
    conn        = MagicMock()
    conn.__enter__ = lambda s: conn
    conn.__exit__  = MagicMock(return_value=False)
    engine.connect.return_value = conn
    return engine


# test the _serialize utility function.
def test_serialize_decimal():
    assert _serialize(Decimal("9.99")) == 9.99

def test_serialize_datetime():
    dt     = datetime(2024, 1, 15, 10, 30, 0)
    result = _serialize(dt)
    assert result == "2024-01-15T10:30:00"

def test_serialize_date():
    d      = date(2024, 1, 15)
    result = _serialize(d)
    assert result == "2024-01-15"

def test_serialize_uuid():
    uid    = UUID("12345678-1234-5678-1234-567812345678")
    result = _serialize(uid)
    assert result == "12345678-1234-5678-1234-567812345678"

def test_serialize_bytes():
    result = _serialize(b"hello")
    assert result == "hello"

def test_serialize_plain_string_passthrough():
    assert _serialize("hello") == "hello"

def test_serialize_int_passthrough():
    assert _serialize(42) == 42

def test_serialize_none_passthrough():
    assert _serialize(None) is None


# connect.

@patch("querymate.core.connection.get_schema_and_prompt")
@patch("querymate.core.connection.create_engine")
def test_connect_postgresql_success(mock_create_engine, mock_schema):
    mock_create_engine.return_value = _mock_engine()
    mock_schema.return_value        = (MOCK_SCHEMA, MOCK_SCHEMA_PROMPT)

    result = connect(
        session_id  = SESSION_ID,
        db_type     = "postgresql",
        credentials = {"url": "postgresql://user:pass@host/db"},
    )

    assert result["status"]      == "ok"
    assert result["db_type"]     == "postgresql"
    assert result["table_count"] == 2
    assert result["error"]       is None

    # clean up
    disconnect(SESSION_ID)


@patch("querymate.core.connection.get_schema_and_prompt")
@patch("querymate.core.connection.create_engine")
def test_connect_mysql_success(mock_create_engine, mock_schema):
    mock_create_engine.return_value = _mock_engine()
    mock_schema.return_value        = (MOCK_SCHEMA, MOCK_SCHEMA_PROMPT)

    result = connect(
        session_id  = "mysql-session",
        db_type     = "mysql",
        credentials = {"url": "mysql+pymysql://user:pass@host/db"},
    )

    assert result["status"]  == "ok"
    assert result["db_type"] == "mysql"
    disconnect("mysql-session")


@patch("querymate.core.connection.get_schema_and_prompt")
@patch("querymate.core.connection.create_engine")
def test_connect_sqlite_success(mock_create_engine, mock_schema):
    mock_create_engine.return_value = _mock_engine()
    mock_schema.return_value        = (MOCK_SCHEMA, MOCK_SCHEMA_PROMPT)

    result = connect(
        session_id  = "sqlite-session",
        db_type     = "sqlite",
        credentials = {"database": "/tmp/test.db"},
    )

    assert result["status"]  == "ok"
    assert result["db_type"] == "sqlite"
    disconnect("sqlite-session")


@patch("querymate.core.connection.create_engine")
def test_connect_unsupported_db_type(mock_create_engine):
    result = connect(
        session_id  = SESSION_ID,
        db_type     = "oracle",
        credentials = {},
    )

    assert result["status"] == "error"
    assert "Unsupported" in result["error"]


@patch("querymate.core.connection.create_engine")
def test_connect_returns_error_on_exception(mock_create_engine):
    mock_create_engine.side_effect = Exception("could not connect to server")

    result = connect(
        session_id  = SESSION_ID,
        db_type     = "postgresql",
        credentials = {"url": "postgresql://bad/url"},
    )

    assert result["status"] == "error"
    assert "could not connect" in result["error"]


# get_session.

def test_get_session_returns_none_for_unknown_id():
    result = get_session("nonexistent-session-id")
    assert result is None


@patch("querymate.core.connection.get_schema_and_prompt")
@patch("querymate.core.connection.create_engine")
def test_get_session_returns_cached_session_after_connect(mock_create_engine, mock_schema):
    mock_create_engine.return_value = _mock_engine()
    mock_schema.return_value        = (MOCK_SCHEMA, MOCK_SCHEMA_PROMPT)

    connect(
        session_id  = "get-session-test",
        db_type     = "postgresql",
        credentials = {"url": "postgresql://user:pass@host/db"},
    )

    session = get_session("get-session-test")

    assert session                  is not None
    assert session["db_type"]       == "postgresql"
    assert session["schema_prompt"] == MOCK_SCHEMA_PROMPT
    disconnect("get-session-test")


# disconnect.

@patch("querymate.core.connection.get_schema_and_prompt")
@patch("querymate.core.connection.create_engine")
def test_disconnect_removes_session(mock_create_engine, mock_schema):
    mock_create_engine.return_value = _mock_engine()
    mock_schema.return_value        = (MOCK_SCHEMA, MOCK_SCHEMA_PROMPT)

    connect(
        session_id  = "disconnect-test",
        db_type     = "postgresql",
        credentials = {"url": "postgresql://user:pass@host/db"},
    )

    result = disconnect("disconnect-test")

    assert result["status"]          == "ok"
    assert get_session("disconnect-test") is None


def test_disconnect_returns_error_for_unknown_session():
    result = disconnect("nonexistent-session-xyz")

    assert result["status"] == "error"
    assert "Session not found" in result["error"]


# execute_query.

def test_execute_query_returns_error_when_no_session():
    result = execute_query("SELECT 1", "nonexistent-session-xyz")

    assert result["rows"]    is None
    assert result["columns"] is None
    assert result["error"]   is not None


@patch("querymate.core.connection.get_schema_and_prompt")
@patch("querymate.core.connection.create_engine")
def test_execute_query_returns_rows_and_columns(mock_create_engine, mock_schema):
    engine      = MagicMock()
    conn        = MagicMock()
    result_mock = MagicMock()

    result_mock.keys.return_value    = ["id", "name"]
    result_mock.fetchall.return_value = [(1, "Alice"), (2, "Bob")]

    conn.__enter__ = lambda s: conn
    conn.__exit__  = MagicMock(return_value=False)
    conn.execute.return_value  = result_mock
    engine.connect.return_value = conn

    mock_create_engine.return_value = engine
    mock_schema.return_value        = (MOCK_SCHEMA, MOCK_SCHEMA_PROMPT)

    connect(
        session_id  = "exec-test",
        db_type     = "postgresql",
        credentials = {"url": "postgresql://user:pass@host/db"},
    )

    result = execute_query("SELECT id, name FROM users", "exec-test")

    assert result["error"]   is None
    assert result["columns"] == ["id", "name"]
    assert len(result["rows"]) == 2
    assert result["rows"][0]   == {"id": 1, "name": "Alice"}
    disconnect("exec-test")


@patch("querymate.core.connection.get_schema_and_prompt")
@patch("querymate.core.connection.create_engine")
def test_execute_query_returns_error_on_db_failure(mock_create_engine, mock_schema):
    engine = MagicMock()
    conn   = MagicMock()
    conn.__enter__ = lambda s: conn
    conn.__exit__  = MagicMock(return_value=False)
    conn.execute.side_effect  = Exception("relation does not exist")
    engine.connect.return_value = conn

    mock_create_engine.return_value = engine
    mock_schema.return_value        = (MOCK_SCHEMA, MOCK_SCHEMA_PROMPT)

    connect(
        session_id  = "exec-error-test",
        db_type     = "postgresql",
        credentials = {"url": "postgresql://user:pass@host/db"},
    )

    result = execute_query("SELECT * FROM nonexistent", "exec-error-test")

    assert result["rows"]  is None
    assert result["error"] is not None
    assert "relation does not exist" in result["error"]
    disconnect("exec-error-test")