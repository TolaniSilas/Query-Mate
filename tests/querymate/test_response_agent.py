"""
tests for agents/response_agent.py — natural language response generation.
mocks all LLM calls so no real API calls are made.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import patch
from querymate.agents.response_agent import generate_response, _build_results_summary


QUESTION = "how many users are there?"
SQL      = "SELECT COUNT(*) FROM users"
ROWS     = [{"count": 42}]


# _build_results_summary.

def test_build_results_summary_empty_rows():
    result = _build_results_summary([], 0, False)
    assert result == "The query returned no results."

def test_build_results_summary_includes_row_count():
    rows   = [{"id": 1, "name": "Alice"}]
    result = _build_results_summary(rows, 1, False)
    assert "Total records returned: 1" in result

def test_build_results_summary_includes_columns():
    rows   = [{"id": 1, "name": "Alice"}]
    result = _build_results_summary(rows, 1, False)
    assert "id" in result
    assert "name" in result

def test_build_results_summary_includes_truncation_notice():
    rows   = [{"id": i} for i in range(50)]
    result = _build_results_summary(rows, 100, True)
    assert "summarise from the first 50" in result

def test_build_results_summary_no_truncation_notice_when_not_truncated():
    rows   = [{"id": 1}]
    result = _build_results_summary(rows, 1, False)
    assert "summarise" not in result

def test_build_results_summary_caps_rows_at_50():
    rows   = [{"id": i} for i in range(100)]
    result = _build_results_summary(rows, 100, True)
    # should only include first 50 in the JSON dump, not all 100
    assert '"id": 49' in result
    assert '"id": 50' not in result


# generate_response — non-ok statuses (no LLM call).

def test_generate_response_cannot_answer_no_llm_call():
    with patch("querymate.agents.response_agent.chat") as mock_chat:
        result = generate_response(QUESTION, SQL, None, "cannot_answer")
        mock_chat.assert_not_called()

    assert result["status"]    == "cannot_answer"
    assert result["row_count"] == 0
    assert result["answer"]    is not None

def test_generate_response_validation_failed_no_llm_call():
    with patch("querymate.agents.response_agent.chat") as mock_chat:
        result = generate_response(QUESTION, SQL, None, "validation_failed", attempts=3)
        mock_chat.assert_not_called()

    assert result["status"] == "validation_failed"
    assert "3 attempt" in result["answer"]

def test_generate_response_error_status_no_llm_call():
    with patch("querymate.agents.response_agent.chat") as mock_chat:
        result = generate_response(QUESTION, SQL, None, "error", attempts=2)
        mock_chat.assert_not_called()

    assert result["status"] == "error"


# generate_response — ok status (LLM call made).

@patch("querymate.agents.response_agent.chat")
def test_generate_response_ok_calls_llm(mock_chat):
    mock_chat.return_value = "There are 42 users in the database."

    result = generate_response(QUESTION, SQL, ROWS, "ok")

    mock_chat.assert_called_once()
    assert result["status"] == "ok"
    assert result["answer"] == "There are 42 users in the database."


@patch("querymate.agents.response_agent.chat")
def test_generate_response_ok_returns_row_count(mock_chat):
    mock_chat.return_value = "There are 42 users."
    rows = [{"count": 42}]

    result = generate_response(QUESTION, SQL, rows, "ok")

    assert result["row_count"] == 1


@patch("querymate.agents.response_agent.chat")
def test_generate_response_truncated_flag_set_correctly(mock_chat):
    mock_chat.return_value = "lots of data"
    rows = [{"id": i} for i in range(60)]

    result = generate_response(QUESTION, SQL, rows, "ok")

    assert result["truncated"]  is True
    assert result["row_count"]  == 60


@patch("querymate.agents.response_agent.chat")
def test_generate_response_not_truncated_under_50_rows(mock_chat):
    mock_chat.return_value = "some data"
    rows = [{"id": i} for i in range(10)]

    result = generate_response(QUESTION, SQL, rows, "ok")

    assert result["truncated"] is False


@patch("querymate.agents.response_agent.chat")
def test_generate_response_handles_empty_rows(mock_chat):
    mock_chat.return_value = "No results were found."

    result = generate_response(QUESTION, SQL, [], "ok")

    assert result["row_count"] == 0
    assert result["status"]    == "ok"


# generate_response — LLM error handling.

@patch("querymate.agents.response_agent.chat")
def test_generate_response_returns_error_on_llm_exception(mock_chat):
    mock_chat.side_effect = Exception("LLM unavailable")

    result = generate_response(QUESTION, SQL, ROWS, "ok")

    assert result["status"] == "error"
    assert result["answer"] is not None
    assert result["row_count"] == 1