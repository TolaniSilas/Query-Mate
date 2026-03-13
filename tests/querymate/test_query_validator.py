"""
tests for core/query_validator.py — the security gate.
these are pure unit tests, no DB or LLM calls needed.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from querymate.core.query_validator import is_safe_query


# safe queries — should all pass.

def test_simple_select():
    safe, reason = is_safe_query("SELECT * FROM users")
    assert safe is True
    assert reason is None

def test_select_with_where():
    safe, reason = is_safe_query("SELECT id, name FROM users WHERE active = true")
    assert safe is True

def test_select_with_join():
    safe, reason = is_safe_query(
        "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"
    )
    assert safe is True

def test_select_with_aggregation():
    safe, reason = is_safe_query(
        "SELECT merchant_id, SUM(amount) FROM transactions GROUP BY merchant_id"
    )
    assert safe is True

def test_select_with_subquery():
    safe, reason = is_safe_query(
        "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE total > 100)"
    )
    assert safe is True


# forbidden queries — should all fail.

def test_delete_rejected():
    safe, reason = is_safe_query("DELETE FROM users WHERE id = 1")
    assert safe is False
    assert reason is not None

def test_drop_rejected():
    safe, reason = is_safe_query("DROP TABLE users")
    assert safe is False

def test_insert_rejected():
    safe, reason = is_safe_query("INSERT INTO users (name) VALUES ('hacker')")
    assert safe is False

def test_update_rejected():
    safe, reason = is_safe_query("UPDATE users SET name = 'hacked' WHERE id = 1")
    assert safe is False

def test_truncate_rejected():
    safe, reason = is_safe_query("TRUNCATE TABLE users")
    assert safe is False

def test_create_rejected():
    safe, reason = is_safe_query("CREATE TABLE evil (id INT)")
    assert safe is False


# comment bypass attempts — should be caught after stripping.

def test_delete_hidden_in_line_comment():
    safe, reason = is_safe_query("SELECT * FROM users -- DELETE FROM users")
    assert safe is False

def test_delete_hidden_in_block_comment():
    safe, reason = is_safe_query("SELECT 1 /* DELETE FROM users */")
    assert safe is False


# case insensitivity.

def test_lowercase_delete_rejected():
    safe, reason = is_safe_query("delete from users")
    assert safe is False

def test_mixed_case_drop_rejected():
    safe, reason = is_safe_query("DrOp TaBlE users")
    assert safe is False