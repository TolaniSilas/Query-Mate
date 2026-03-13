"""
tests for agents/validator_agent.py — the SQL quality gate.
mocks all LLM calls so no real API calls are made.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import patch
from querymate.agents.validator_agent import validate, _extract_field


SCHEMA_PROMPT = "CREATE TABLE users (id INT, name TEXT)"
QUESTION      = "how many users are there?"
SQL           = "SELECT COUNT(*) FROM users"


# _extract_field.
def test_extract_field_verdict():
    text = "VERDICT: PASS\nREASON: looks good\nFEEDBACK: None"
    assert _extract_field(text, "VERDICT") == "PASS"

def test_extract_field_reason():
    text = "VERDICT: FAIL\nREASON: missing GROUP BY\nFEEDBACK: add GROUP BY merchant_id"
    assert _extract_field(text, "REASON") == "missing GROUP BY"

def test_extract_field_feedback():
    text = "VERDICT: FAIL\nREASON: wrong table\nFEEDBACK: use the orders table instead"
    assert _extract_field(text, "FEEDBACK") == "use the orders table instead"

def test_extract_field_returns_none_when_missing():
    text = "VERDICT: PASS"
    assert _extract_field(text, "FEEDBACK") is None

def test_extract_field_case_insensitive_key():
    text = "verdict: PASS\nreason: good\nfeedback: None"
    assert _extract_field(text, "VERDICT") == "PASS"

def test_extract_field_with_colon_in_value():
    text = "FEEDBACK: use JOIN: orders ON orders.user_id = users.id"
    result = _extract_field(text, "FEEDBACK")
    assert result == "use JOIN: orders ON orders.user_id = users.id"


# validate — PASS verdict.
@patch("querymate.agents.validator_agent.chat")
def test_validate_returns_ok_on_pass(mock_chat):
    mock_chat.return_value = "VERDICT: PASS\nREASON: SQL is correct\nFEEDBACK: None"

    result = validate(QUESTION, SQL, SCHEMA_PROMPT)

    assert result["status"]   == "ok"
    assert result["feedback"] is None
    assert result["reason"]   == "SQL is correct"


@patch("querymate.agents.validator_agent.chat")
def test_validate_pass_case_insensitive(mock_chat):
    mock_chat.return_value = "VERDICT: pass\nREASON: fine\nFEEDBACK: None"

    result = validate(QUESTION, SQL, SCHEMA_PROMPT)

    assert result["status"] == "ok"


# validate — FAIL verdict.
@patch("querymate.agents.validator_agent.chat")
def test_validate_returns_rejected_on_fail(mock_chat):
    mock_chat.return_value = (
        "VERDICT: FAIL\n"
        "REASON: missing GROUP BY clause\n"
        "FEEDBACK: add GROUP BY merchant_id after the WHERE clause"
    )

    result = validate(QUESTION, SQL, SCHEMA_PROMPT)

    assert result["status"]   == "rejected"
    assert result["reason"]   == "missing GROUP BY clause"
    assert result["feedback"] == "add GROUP BY merchant_id after the WHERE clause"


@patch("querymate.agents.validator_agent.chat")
def test_validate_rejected_includes_feedback(mock_chat):
    mock_chat.return_value = "VERDICT: FAIL\nREASON: wrong table\nFEEDBACK: use orders table"

    result = validate(QUESTION, SQL, SCHEMA_PROMPT)

    assert result["feedback"] is not None
    assert "orders" in result["feedback"]


@patch("querymate.agents.validator_agent.chat")
def test_validate_rejected_has_fallback_reason(mock_chat):

    # LLM returns FAIL but no REASON line
    mock_chat.return_value = "VERDICT: FAIL\nFEEDBACK: fix the join"

    result = validate(QUESTION, SQL, SCHEMA_PROMPT)

    assert result["status"] == "rejected"
    assert result["reason"] is not None


# validate — error handling.
@patch("querymate.agents.validator_agent.chat")
def test_validate_returns_error_on_exception(mock_chat):
    mock_chat.side_effect = Exception("LLM unavailable")

    result = validate(QUESTION, SQL, SCHEMA_PROMPT)

    assert result["status"]   == "error"
    assert result["feedback"] is None
    assert "LLM unavailable" in result["reason"]


@patch("querymate.agents.validator_agent.chat")
def test_validate_calls_chat_with_question_and_sql(mock_chat):
    mock_chat.return_value = "VERDICT: PASS\nREASON: ok\nFEEDBACK: None"

    validate(QUESTION, SQL, SCHEMA_PROMPT)

    call_args = mock_chat.call_args
    user_arg  = call_args.kwargs.get("user") or call_args.args[1]
    assert QUESTION in user_arg
    assert SQL      in user_arg