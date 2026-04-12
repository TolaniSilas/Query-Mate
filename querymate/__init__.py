"""
querymate is a natural language Python package for querying relational databases. It currently supports
MySQL, PostgreSQL, and SQLite, and enforces security at both the 'connection' level and 'type of query'
level - ensuring only safe, read-only operations reach your database.


how to use:
    from querymate import QueryMate

    query_mate = QueryMate(
        user_id = "user_abc123",
        database_url = "postgresql://user:password@host/dbname?sslmode=require",
        db_type = "postgresql",
    )

    result = query_mate.ask("which merchant had the highest revenue last month?")

    print(result.answer)    # this is the natural language answer
    print(result.sql)    # the SQL that was generated and executed
    print(result.rows)    # raw result rows
    print(result.status)    # "ok" | "cannot_answer" | "validation_failed" | "error"

    query_mate.disconnect()  # this terminates the database connection.


required environment variables:
    DATABASE_URL -> the database you want to query.
    MEMORY_DATABASE_URL -> QueryMate's own Postgres for conversation history.
    REDIS_URL -> Redis instance for QueryMate's session caching.
"""


import uuid
from querymate.core.connection import connect, disconnect, get_session
from querymate.core.pipeline import run_pipeline
from querymate.core.logger import get_logger
from querymate.memory.models import create_tables
from querymate.memory.store import ensure_user, close_active_session, create_session, end_session, save_message
from querymate.memory.context import build_context


logger = get_logger(__name__)


class QueryResult:
    """
    the result object returned from QueryMate.ask().
    gives clean attribute access to everything the pipeline produced.
    """

    def __init__(self, data: dict):
        self.answer = data.get("answer")
        self.sql = data.get("sql")
        self.rows = data.get("rows")
        self.row_count= data.get("row_count", 0)
        self.truncated = data.get("truncated", False)
        self.attempts = data.get("attempts", 1)
        self.status = data.get("status")
        self.error = data.get("error")

    def __repr__(self):
        return (
            f"QueryResult("
            f"status={self.status!r},"
            f"row_count={self.row_count},"
            f"attempts={self.attempts}"
            f")"
        )


class QueryMate:
    """
    the main entry point for the querymate package. it connects to a database once, caches
    the schema, and exposes a single .ask() method that converts natural language questions into answers.
    conversation history is persisted per user so follow-up questions resolve correctly.

    params
        user_id: stable identifier for the user, provided by the developer's own auth system.
                 querymate uses this to persist and retrieve conversation history.
        database_url: full connection URL for postgresql or mysql.
                    for sqlite, pass the file path via sqlite_path instead.
        db_type: "postgresql" | "mysql" | "sqlite"
        sqlite_path: absolute path to the sqlite file (sqlite only)


    for usage, here is an instance:
        # postgresql / mysql
        query_mate = QueryMate(
            user_id = "user_abc123",
            database_url = "postgresql://user:pass@host/dbname?sslmode=require",
            db_type = "postgresql",
        )

        # sqlite
        query_mate = QueryMate(
            user_id = "user_abc123",
            db_type = "sqlite",
            sqlite_path = "/path/to/database.sqlite",
        )
    """

    def __init__(self, user_id: str, db_type: str, database_url: str | None = None, sqlite_path: str | None = None):

        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty.")

        self._user_id = user_id.strip()
        self._session_id = str(uuid.uuid4())
        self._db_type = db_type.lower().strip()
        self._connected = False

        credentials = self._build_credentials(database_url, sqlite_path)

        logger.info("querymate | initialising | user: %s | db_type: %s", self._user_id, self._db_type)

        # initialise memory store and session cache.
        # errors here are caught and re-raised with clear, actionable messages.
        try:
            create_tables()
            ensure_user(self._user_id)
            close_active_session(self._user_id)
            create_session(self._user_id, self._session_id)
            
        except ConnectionError:
            raise

        except Exception as e:
            raise ConnectionError(
                f"QueryMate failed to initialise the memory store or session cache.\n"
                f"Ensure MEMORY_DATABASE_URL and REDIS_URL are correctly set in your .env.\n"
                f"Error: {e}"
            ) from e

        result = connect(
            session_id = self._session_id,
            db_type = self._db_type,
            credentials = credentials,
        )

        if result["status"] != "ok":
            raise ConnectionError(
                f"Failed to connect to database: {result['error']}"
            )

        self._connected = True
        self.db_type = result["db_type"]
        self.table_count = result["table_count"]
        self.tables = result["tables"]

        logger.info("querymate | connected | tables: %d", self.table_count)


    def ask(self, question: str) -> QueryResult:
        """
        query the database with natural language and return an answer.
        conversation history from this session is automatically included as context.

        parameters
            question: plain english question about the connected database

        returns
            QueryResult with .answer, .sql, .rows, .status, .error

        raises
            RuntimeError: if called after disconnect()
            ValueError: if question is empty
        """

        if not self._connected:
            raise RuntimeError(
                "QueryMate is not connected. "
                "Create a new QueryMate instance to reconnect."
            )

        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty.")

        session = get_session(self._session_id)

        if not session:
            raise RuntimeError("Session expired. Create a new QueryMate instance to reconnect.")

        logger.info("querymate | ask | user: %s | question: %s", self._user_id, question)

        # build context from prior exchanges in this session.
        conversation_context = build_context(self._session_id)

        # persist the user's question before running the pipeline.
        save_message(self._session_id, role="user", content=question)

        result = run_pipeline(
            question = question,
            schema_prompt = session["schema_prompt"],
            db_type = self._db_type,
            session_id = self._session_id,
            conversation_context = conversation_context,
        )

        # persist the assistant's answer and the SQL.
        save_message(
            self._session_id,
            role = "assistant",
            content = result.get("answer") or "",
            sql = result.get("sql"),
        )

        return QueryResult(result)


    def disconnect(self):
        """
        closes the database connection, ends the memory session, and clears the cache.
        the instance cannot be used after this is called.
        """

        if self._connected:
            end_session(self._session_id)
            disconnect(self._session_id)
            self._connected = False
            logger.info("querymate | disconnected | session: %s", self._session_id)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        for usage as a context manager:
        """

        self.disconnect()


    def _build_credentials(self, database_url: str | None, sqlite_path: str | None) -> dict:

        if self._db_type == "sqlite":
            if not sqlite_path:
                raise ValueError("sqlite_path is required for db_type='sqlite'.")
            return {"database": sqlite_path}

        if not database_url:
            raise ValueError("database_url is required for postgresql and mysql.")

        return {"url": database_url}


    def __repr__(self):
        status = "connected" if self._connected else "disconnected"

        return (
            f"QueryMate("
            f"user_id={self._user_id!r}, "
            f"db_type={self.db_type!r}, "
            f"tables={self.table_count}, "
            f"status={status!r}"
            f")"
        )