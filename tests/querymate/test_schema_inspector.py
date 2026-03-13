"""
tests for core/schema_inspector.py — database schema inspection.
mocks sqlalchemy so no real DB calls are made.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import patch, MagicMock, PropertyMock


# build_llm_prompt.
def test_build_llm_prompt_includes_table_names():
    from querymate.core.schema_inspector import build_llm_prompt

    schema = {
        "tables": {
            "users": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "name", "type": "TEXT", "nullable": True, "primary_key": False},
                ],
                "row_count": 100,
                "sample_rows": [],
                "indexes": [],
            }
        }
    }

    prompt = build_llm_prompt(schema)

    assert "users" in prompt
    assert "CREATE TABLE" in prompt


def test_build_llm_prompt_includes_column_names():
    from querymate.core.schema_inspector import build_llm_prompt

    schema = {
        "tables": {
            "orders": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "user_id", "type": "INTEGER", "nullable": False, "primary_key": False},
                    {"name": "total", "type": "NUMERIC", "nullable": True, "primary_key": False},
                ],
                "row_count":   50,
                "sample_rows": [],
                "indexes":     [],
            }
        }
    }

    prompt = build_llm_prompt(schema)

    assert "id" in prompt
    assert "user_id" in prompt
    assert "total" in prompt


def test_build_llm_prompt_includes_sample_rows():
    from querymate.core.schema_inspector import build_llm_prompt

    schema = {
        "tables": {
            "users": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "name", "type": "TEXT", "nullable": True, "primary_key": False},
                ],
                "row_count":   3,
                "sample_rows": [
                    {"id": 1, "name": "Alice"},
                    {"id": 2, "name": "Bob"},
                ],
                "indexes": [],
            }
        }
    }

    prompt = build_llm_prompt(schema)

    assert "Alice" in prompt
    assert "Bob" in prompt


def test_build_llm_prompt_handles_empty_schema():
    from querymate.core.schema_inspector import build_llm_prompt

    schema = {"tables": {}}
    prompt = build_llm_prompt(schema)

    assert isinstance(prompt, str)


def test_build_llm_prompt_marks_primary_key():
    from querymate.core.schema_inspector import build_llm_prompt

    schema = {
        "tables": {
            "users": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                ],
                "row_count": 0,
                "sample_rows": [],
                "indexes": [],
            }
        }
    }

    prompt = build_llm_prompt(schema)

    assert "PRIMARY KEY" in prompt.upper()


def test_build_llm_prompt_with_relevant_tables_filters_schema():
    from querymate.core.schema_inspector import build_llm_prompt

    schema = {
        "tables": {
            "users":    {
                "columns": [{"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True}],
                "row_count":   0,
                "sample_rows": [],
                "indexes": [],
            },
            "products": {
                "columns": [{"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True}],
                "row_count": 0,
                "sample_rows": [],
                "indexes": [],
            },
        }
    }

    prompt = build_llm_prompt(schema, relevant_tables=["users"])

    assert "users" in prompt
    assert "products" not in prompt


# get_schema_and_prompt.
@patch("querymate.core.schema_inspector.inspect_database")
@patch("querymate.core.schema_inspector.build_llm_prompt")
def test_get_schema_and_prompt_returns_tuple(mock_prompt, mock_inspect):
    mock_inspect.return_value = {"tables": {"users": {}}}
    mock_prompt.return_value = "CREATE TABLE users (...)"

    from querymate.core.schema_inspector import get_schema_and_prompt
    schema, prompt = get_schema_and_prompt("postgresql://user:pass@host/db")

    assert schema == {"tables": {"users": {}}}
    assert prompt == "CREATE TABLE users (...)"


@patch("querymate.core.schema_inspector.inspect_database")
@patch("querymate.core.schema_inspector.build_llm_prompt")
def test_get_schema_and_prompt_calls_inspect_with_connection_string(mock_prompt, mock_inspect):
    mock_inspect.return_value = {"tables": {}}
    mock_prompt.return_value = ""

    from querymate.core.schema_inspector import get_schema_and_prompt
    get_schema_and_prompt("postgresql://user:pass@host/db")

    mock_inspect.assert_called_once_with("postgresql://user:pass@host/db")


# inspect_database - structure validation.
@patch("querymate.core.schema_inspector.create_engine")
@patch("querymate.core.schema_inspector.inspect")
def test_inspect_database_returns_tables_key(mock_inspect_fn, mock_create_engine):
    mock_engine = MagicMock()
    mock_inspector = MagicMock()
    mock_conn = MagicMock()

    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
    mock_engine.connect.return_value.__exit__  = MagicMock(return_value=False)
    mock_inspect_fn.return_value = mock_inspector

    mock_inspector.get_table_names.return_value = ["users"]
    mock_inspector.get_columns.return_value = [
        {"name": "id", "type": MagicMock(__str__=lambda s: "INTEGER"), "nullable": False}
    ]
    mock_inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}
    mock_inspector.get_indexes.return_value = []
    mock_inspector.get_foreign_keys.return_value = []

    mock_conn.execute.return_value.fetchall.return_value = []
    mock_conn.execute.return_value.scalar.return_value = 0

    from querymate.core.schema_inspector import inspect_database
    result = inspect_database("sqlite:///test.db")

    assert "tables" in result