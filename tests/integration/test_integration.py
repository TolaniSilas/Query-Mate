"""
integration tests for the full querymate pipeline.

these tests require a real database connection.
set DATABASE_URL in your .env before running.

run with:
    uv run pytest tests/integration/ -v

WARNING: never run against a production database.
         use a dedicated test database with sample data.
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from dotenv import load_dotenv
from querymate.core.connection import connect, disconnect
from querymate import QueryMate
from querymate.core.connection import get_session
from querymate.core.query_validator import is_safe_query
from querymate.core.connection import execute_query
from fastapi.testclient import TestClient
import importlib
import serving.main as main_module




load_dotenv()


# skip all integration tests if DATABASE_URL is not set.
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set - skipping integration tests.",
)

DB_TYPE = os.environ.get("DB_TYPE", "postgresql")
DATABASE_URL = os.environ.get("DATABASE_URL", "")


# test_full_pipeline.py
class TestFullPipeline:

    def setup_method(self):

        self.session_id = str(uuid.uuid4())
        result = connect(
            session_id = self.session_id,
            db_type = DB_TYPE,
            credentials = {"url": DATABASE_URL},
        )

        if result["status"] != "ok":
            pytest.skip(f"could not connect to database: {result['error']}")

        self.tables = result["tables"]

    def teardown_method(self):
        disconnect(self.session_id)


    def test_connect_returns_tables(self):
        assert isinstance(self.tables, list)
        assert len(self.tables) > 0


    def test_ask_simple_count_question(self):

        with QueryMate(db_type=DB_TYPE, database_url=DATABASE_URL) as qm:
            table = qm.tables[0]
            result = qm.ask(f"how many records are in {table}?")

        assert result.status in ("ok", "cannot_answer")
        if result.status == "ok":
            assert result.answer  is not None
            assert result.sql     is not None
            assert result.sql.strip().upper().startswith("SELECT")


    def test_ask_unanswerable_question(self):

        with QueryMate(db_type=DB_TYPE, database_url=DATABASE_URL) as qm:
            result = qm.ask(
                "what is the current price of bitcoin in euros right now today?"
            )

        assert result.status in ("cannot_answer", "ok")


    def test_disconnect_clears_session(self):

        qm = QueryMate(db_type=DB_TYPE, database_url=DATABASE_URL)
        sid = qm._session_id
        qm.disconnect()

        assert get_session(sid) is None


    def test_generated_sql_is_select_only(self):

        with QueryMate(db_type=DB_TYPE, database_url=DATABASE_URL) as qm:
            table  = qm.tables[0]
            result = qm.ask(f"show me the first 5 rows from {table}")

        if result.sql:
            assert result.sql.strip().upper().startswith("SELECT")


# test_read_only_enforcement.py
class TestReadOnlyEnforcement:

    def setup_method(self):

        self.session_id = str(uuid.uuid4())
        result = connect(
            session_id  = self.session_id,
            db_type     = DB_TYPE,
            credentials = {"url": DATABASE_URL},
        )

        if result["status"] != "ok":
            pytest.skip(f"could not connect to database: {result['error']}")

    def teardown_method(self):
        disconnect(self.session_id)


    def test_security_gate_rejects_delete(self):

        safe, reason = is_safe_query("DELETE FROM users WHERE id = 1")

        assert safe is False
        assert reason is not None


    def test_security_gate_rejects_insert(self):

        safe, reason = is_safe_query("INSERT INTO users (name) VALUES ('hacker')")

        assert safe is False


    def test_security_gate_rejects_update(self):

        safe, reason = is_safe_query("UPDATE users SET name = 'hacked'")

        assert safe is False


    def test_security_gate_rejects_drop(self):

        safe, reason = is_safe_query("DROP TABLE users")

        assert safe is False


    def test_connection_level_rejects_raw_insert(self):

        sql  = "INSERT INTO _test_table (id) VALUES (1)"
        safe, _ = is_safe_query(sql)

        # should be caught at security gate before reaching DB
        assert safe is False


    def test_pipeline_rejects_delete_question(self):

        with QueryMate(db_type=DB_TYPE, database_url=DATABASE_URL) as qm:
            result = qm.ask("delete all records from the database")

        # pipeline should either refuse to generate DELETE SQL or reject it
        assert result.status in ("security_rejected", "cannot_answer", "ok")
        if result.sql:
            assert "DELETE" not in result.sql.upper()



# test_api_end_to_end.py
class TestAPIEndToEnd:

    def setup_method(self):
        
        importlib.reload(main_module)
        
        self.client = TestClient(main_module.app)


    def test_full_connect_query_disconnect_flow(self):
        
        # connect to the database.
        connect_response = self.client.post("/api/connect", json={
            "db_type": DB_TYPE,
            "database_url": DATABASE_URL,
        })

        assert connect_response.status_code == 200
        connect_data = connect_response.json()
        assert connect_data["status"] == "ok"
        assert connect_data["session_id"] is not None

        session_id = connect_data["session_id"]

        # query the database.
        table = connect_data["tables"][0] if connect_data["tables"] else None
        if table:
            query_response = self.client.post("/api/query", json={
                "session_id": session_id,
                "question": f"how many records are in {table}?",
            })

            assert query_response.status_code == 200
            query_data = query_response.json()
            assert query_data["status"] in ("ok", "cannot_answer", "validation_failed")

        # step 3 — disconnect
        disconnect_response = self.client.delete(f"/api/disconnect?session_id={session_id}")

        assert disconnect_response.status_code == 200
        assert disconnect_response.json()["status"] == "ok"


    def test_query_without_connect_returns_error(self):
        response = self.client.post("/api/query", json={
            "session_id": "nonexistent-session-id-xyz",
            "question": "how many users?",
        })

        data = response.json()
        assert data["status"] == "error"
        assert "Session not found" in data["error"]


    def test_schema_returns_correct_tables_after_connect(self):
        connect_response = self.client.post("/api/connect", json={
            "db_type": DB_TYPE,
            "database_url": DATABASE_URL,
        })

        session_id = connect_response.json()["session_id"]

        schema_response = self.client.get(f"/api/schema?session_id={session_id}")

        assert schema_response.status_code == 200
        data = schema_response.json()
        assert data["status"] == "ok"
        assert data["tables"] is not None
        assert len(data["tables"]) > 0

        self.client.delete(f"/api/disconnect?session_id={session_id}")


    def test_expired_session_returns_meaningful_error(self):
        # connect then immediately disconnect
        connect_response = self.client.post("/api/connect", json={
            "db_type": DB_TYPE,
            "database_url": DATABASE_URL,
        })

        session_id = connect_response.json()["session_id"]
        self.client.delete(f"/api/disconnect?session_id={session_id}")

        # now try to query the disconnected session
        query_response = self.client.post("/api/query", json={
            "session_id": session_id,
            "question": "how many users?",
        })

        data = query_response.json()
        assert data["status"] == "error"
        assert data["error"] is not None