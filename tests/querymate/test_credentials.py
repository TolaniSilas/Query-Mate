"""
tests for security/credentials.py — environment variable credential loading.
uses monkeypatching to set/unset env vars without touching the real environment.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import patch


# get_db_credentials — postgresql.
def test_get_db_credentials_postgresql_returns_url():
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}):
        from querymate.security.credentials import get_db_credentials
        result = get_db_credentials("postgresql")

    assert result == {"url": "postgresql://user:pass@host/db"}


def test_get_db_credentials_mysql_returns_url():
    with patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://user:pass@host/db"}):
        from querymate.security.credentials import get_db_credentials
        result = get_db_credentials("mysql")

    assert result == {"url": "mysql+pymysql://user:pass@host/db"}


def test_get_db_credentials_postgresql_uppercase_accepted():
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}):
        from querymate.security.credentials import get_db_credentials
        result = get_db_credentials("POSTGRESQL")

    assert "url" in result


def test_get_db_credentials_raises_key_error_when_database_url_missing():
    with patch.dict(os.environ, {}, clear=True):
        # remove DATABASE_URL if present
        os.environ.pop("DATABASE_URL", None)
        from querymate.security.credentials import get_db_credentials
        with pytest.raises(KeyError, match="DATABASE_URL"):
            get_db_credentials("postgresql")


def test_get_db_credentials_raises_value_error_for_unsupported_type():
    from querymate.security.credentials import get_db_credentials
    with pytest.raises(ValueError, match="Unsupported database type"):
        get_db_credentials("oracle")


# get_db_credentials — sqlite.
def test_get_db_credentials_sqlite_returns_database_path(tmp_path):
    db_file = tmp_path / "test.db"
    db_file.write_text("")  # create the file

    with patch.dict(os.environ, {"DB_SQLITE_PATH": str(db_file)}):
        from querymate.security.credentials import get_db_credentials
        result = get_db_credentials("sqlite")

    assert "database" in result
    assert str(db_file) in result["database"]


def test_get_db_credentials_sqlite_raises_file_not_found(tmp_path):
    nonexistent = str(tmp_path / "does_not_exist.db")

    with patch.dict(os.environ, {"DB_SQLITE_PATH": nonexistent}):
        from querymate.security.credentials import get_db_credentials
        with pytest.raises(FileNotFoundError, match="not found"):
            get_db_credentials("sqlite")


def test_get_db_credentials_sqlite_raises_when_path_missing():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("DB_SQLITE_PATH", None)
        from querymate.security.credentials import get_db_credentials
        with pytest.raises(KeyError, match="DB_SQLITE_PATH"):
            get_db_credentials("sqlite")


# validate_env.
def test_validate_env_postgresql_valid():
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}):
        from querymate.security.credentials import validate_env
        result = validate_env("postgresql")

    assert result["valid"]   is True
    assert result["missing"] == []
    assert result["db_type"] == "postgresql"


def test_validate_env_postgresql_missing_database_url():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("DATABASE_URL", None)
        from querymate.security.credentials import validate_env
        result = validate_env("postgresql")

    assert result["valid"]          is False
    assert "DATABASE_URL" in result["missing"]


def test_validate_env_sqlite_valid(tmp_path):
    db_file = tmp_path / "test.db"
    db_file.write_text("")

    with patch.dict(os.environ, {"DB_SQLITE_PATH": str(db_file)}):
        from querymate.security.credentials import validate_env
        result = validate_env("sqlite")

    assert result["valid"]   is True
    assert result["missing"] == []


def test_validate_env_sqlite_missing_path():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("DB_SQLITE_PATH", None)
        from querymate.security.credentials import validate_env
        result = validate_env("sqlite")

    assert result["valid"]           is False
    assert "DB_SQLITE_PATH" in result["missing"]


def test_validate_env_mysql_valid():
    with patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://user:pass@host/db"}):
        from querymate.security.credentials import validate_env
        result = validate_env("mysql")

    assert result["valid"] is True