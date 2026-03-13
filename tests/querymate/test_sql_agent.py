"""
tests for agents/sql_agent.py — SQL generation and retry loop.
mocks all LLM calls so no real API calls are made.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import patch, MagicMock
from querymate.agents.sql_agent import generate_sql, run_sql_agent, _extract_sql


SCHEMA_PROMPT = "CREATE TABLE users (id INT, name TEXT, active BOOLEAN)"
QUESTION      = "how many active users are there?"
VALID_SQL     = "SELECT COUNT(*) FROM users WHERE active = true"


# _extract_sql.

def test_extract_sql_strips_markdown_fences():
    raw = "```sql\nSELECT * FROM users\n```"
    assert _extract_sql(raw) == "SELECT * FROM users"

def test_extract_sql_strips_plain_fences():
    raw = "```\nSELECT * FROM users\n```"
    assert _extract_sql(raw) == "SELECT * FROM users"

def test_extract_sql_passthrough_clean_sql():
    raw = "SELECT * FROM users"
    assert _extract_sql(raw) == "SELECT * FROM users"

def test_extract_sql_case_insensitive_fence():
    raw = "```SQL\nSELECT 1\n```"
    assert _extract_sql(raw) == "SELECT 1"


# generate_sql.

@patch("querymate.agents.sql_agent.chat")
def test_generate_sql_returns_ok(mock_chat):
    mock_chat.return_value = VALID_SQL

    result = generate_sql(QUESTION, SCHEMA_PROMPT, "postgresql")

    assert result["status"] == "ok"
    assert result["sql"]    == VALID_SQL
    assert result["error"]  is None


@patch("querymate.agents.sql_agent.chat")
def test_generate_sql_returns_cannot_answer(mock_chat):
    mock_chat.return_value = "CANNOT_ANSWER"

    result = generate_sql("what is the weather today?", SCHEMA_PROMPT, "postgresql")

    assert result["status"] == "cannot_answer"
    assert result["sql"]    is None


@patch("querymate.agents.sql_agent.chat")
def test_generate_sql_cannot_answer_case_insensitive(mock_chat):
    mock_chat.return_value = "cannot_answer"

    result = generate_sql("irrelevant question", SCHEMA_PROMPT, "postgresql")

    assert result["status"] == "cannot_answer"


@patch("querymate.agents.sql_agent.chat")
def test_generate_sql_returns_error_on_exception(mock_chat):
    mock_chat.side_effect = Exception("API down")

    result = generate_sql(QUESTION, SCHEMA_PROMPT, "postgresql")

    assert result["status"] == "error"
    assert result["sql"]    is None
    assert "API down" in result["error"]


@patch("querymate.agents.sql_agent.chat")
def test_generate_sql_strips_markdown_from_response(mock_chat):
    mock_chat.return_value = f"```sql\n{VALID_SQL}\n```"

    result = generate_sql(QUESTION, SCHEMA_PROMPT, "postgresql")

    assert result["status"] == "ok"
    assert result["sql"]    == VALID_SQL


@patch("querymate.agents.sql_agent.chat")
def test_generate_sql_appends_feedback_on_retry(mock_chat):
    mock_chat.return_value = VALID_SQL
    feedback = "missing GROUP BY clause"

    generate_sql(QUESTION, SCHEMA_PROMPT, "postgresql", feedback=feedback)

    call_args = mock_chat.call_args
    user_arg  = call_args.kwargs.get("user") or call_args.args[1]
    assert feedback in user_arg


# run_sql_agent.

def _make_validator_ok():
    return lambda q, s, sp: {"status": "ok", "reason": "looks good", "feedback": None}

def _make_validator_fail(feedback="fix the JOIN"):
    return lambda q, s, sp: {"status": "rejected", "reason": "wrong", "feedback": feedback}

def _make_executor_ok(rows=None):
    return lambda sql: {"rows": rows or [{"count": 5}], "columns": ["count"], "error": None}

def _make_executor_error(msg="syntax error"):
    return lambda sql: {"rows": None, "columns": None, "error": msg}


@patch("querymate.agents.sql_agent.chat")
def test_run_sql_agent_success_on_first_attempt(mock_chat):
    mock_chat.return_value = VALID_SQL

    result = run_sql_agent(
        question      = QUESTION,
        schema_prompt = SCHEMA_PROMPT,
        db_type       = "postgresql",
        validator_fn  = _make_validator_ok(),
        executor_fn   = _make_executor_ok(),
    )

    assert result["status"]   == "ok"
    assert result["sql"]      == VALID_SQL
    assert result["attempts"] == 1
    assert result["error"]    is None


@patch("querymate.agents.sql_agent.chat")
def test_run_sql_agent_retries_on_validation_rejection(mock_chat):
    mock_chat.return_value = VALID_SQL

    call_count = {"n": 0}
    def validator(q, s, sp):
        call_count["n"] += 1
        if call_count["n"] < 2:
            return {"status": "rejected", "reason": "wrong", "feedback": "fix it"}
        return {"status": "ok", "reason": "good", "feedback": None}

    result = run_sql_agent(
        question      = QUESTION,
        schema_prompt = SCHEMA_PROMPT,
        db_type       = "postgresql",
        validator_fn  = validator,
        executor_fn   = _make_executor_ok(),
    )

    assert result["status"]   == "ok"
    assert result["attempts"] == 2


@patch("querymate.agents.sql_agent.chat")
def test_run_sql_agent_retries_on_execution_error(mock_chat):
    mock_chat.return_value = VALID_SQL

    call_count = {"n": 0}
    def executor(sql):
        call_count["n"] += 1
        if call_count["n"] < 2:
            return {"rows": None, "columns": None, "error": "syntax error"}
        return {"rows": [{"count": 1}], "columns": ["count"], "error": None}

    result = run_sql_agent(
        question      = QUESTION,
        schema_prompt = SCHEMA_PROMPT,
        db_type       = "postgresql",
        validator_fn  = _make_validator_ok(),
        executor_fn   = executor,
    )

    assert result["status"]   == "ok"
    assert result["attempts"] == 2


@patch("querymate.agents.sql_agent.chat")
def test_run_sql_agent_returns_validation_failed_after_max_retries(mock_chat):
    mock_chat.return_value = VALID_SQL

    result = run_sql_agent(
        question      = QUESTION,
        schema_prompt = SCHEMA_PROMPT,
        db_type       = "postgresql",
        validator_fn  = _make_validator_fail(),
        executor_fn   = _make_executor_ok(),
    )

    assert result["status"]   == "validation_failed"
    assert result["attempts"] == 3
    assert result["error"]    is not None


@patch("querymate.agents.sql_agent.chat")
def test_run_sql_agent_returns_cannot_answer_without_retrying(mock_chat):
    mock_chat.return_value = "CANNOT_ANSWER"

    result = run_sql_agent(
        question      = QUESTION,
        schema_prompt = SCHEMA_PROMPT,
        db_type       = "postgresql",
        validator_fn  = _make_validator_ok(),
        executor_fn   = _make_executor_ok(),
    )

    assert result["status"]   == "cannot_answer"
    assert result["attempts"] == 1
    assert mock_chat.call_count == 1


@patch("querymate.agents.sql_agent.chat")
def test_run_sql_agent_returns_error_on_llm_failure(mock_chat):
    mock_chat.side_effect = Exception("LLM unavailable")

    result = run_sql_agent(
        question      = QUESTION,
        schema_prompt = SCHEMA_PROMPT,
        db_type       = "postgresql",
        validator_fn  = _make_validator_ok(),
        executor_fn   = _make_executor_ok(),
    )

    assert result["status"] == "error"
    assert result["sql"]    is None