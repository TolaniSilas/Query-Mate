"""
querymate is a natural language Python package for querying relational databases. It currently supports 
MySQL, PostgreSQL, and SQLite, and enforces security at both the 'connection' level and 'type of query' 
level - ensuring only safe, read-only operations reach your database.

usage:
    from querymate import QueryMate

    qm = QueryMate(
        database_url = "postgresql://user:password@host/dbname?sslmode=require",
        db_type = "postgresql",
    )

    result = qm.ask("which merchant had the highest revenue last month?")

    print(result.answer)    # this is the natural language answer
    print(result.sql)       # the SQL that was generated and executed
    print(result.rows)      # raw result rows
    print(result.status)    # "ok" | "cannot_answer" | "validation_failed" | "error"

    qm.disconnect()  # this terminates the database connection.
"""

import uuid
from querymate.core.connection import connect, disconnect, get_session
from querymate.core.pipeline import run_pipeline
from querymate.core.logger import get_logger


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
        self.row_count = data.get("row_count", 0)
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
    the main entry point for the querymate package.

    connects to a database once, caches the schema, and exposes a single
    .ask() method that converts natural language questions into answers.

    parameters
    ----------
    database_url : full connection URL for postgresql or mysql.
                   for sqlite, pass the file path via sqlite_path instead.
    db_type      : "postgresql" | "mysql" | "sqlite"
    sqlite_path  : absolute path to the sqlite file (sqlite only)

    
    for usage, here is an instance: 
    -------
    # postgresql / mysql
    qm = QueryMate(
        database_url = "postgresql://user:pass@host/dbname?sslmode=require",
        db_type = "postgresql",
    )

    # sqlite
    qm = QueryMate(
        db_type = "sqlite",
        sqlite_path = "/path/to/database.sqlite",
    )
    """

    def __init__(self, db_type: str, database_url: str | None = None, sqlite_path: str | None = None):

        self._session_id = str(uuid.uuid4())
        self._db_type = db_type.lower().strip()
        self._connected = False

        credentials = self._build_credentials(database_url, sqlite_path)

        logger.info("querymate | initialising | db_type: %s", self._db_type)

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
        converts a natural language question into an answer.

        parameters
        ----------
        question : plain english question about the connected database

        returns
        -------
        QueryResult with .answer, .sql, .rows, .status, .error

        raises
        ------
        RuntimeError   if called after disconnect()
        ValueError     if question is empty
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

        logger.info("querymate | ask | question: %s", question)

        result = run_pipeline(
            question = question,
            schema_prompt = session["schema_prompt"],
            db_type = self._db_type,
            session_id = self._session_id,
        )

        return QueryResult(result)


    def disconnect(self):
        """
        closes the database connection and clears the session.
        the instance cannot be used after this is called.
        """
        if self._connected:
            disconnect(self._session_id)
            self._connected = False
            logger.info("querymate | disconnected | session: %s", self._session_id)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        this supports usage as a context manager:

        with QueryMate(...) as qm:
            result = qm.ask("your question")

        """

        # terminate the database connection.
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
            f"db_type={self.db_type!r}, "
            f"tables={self.table_count}, "
            f"status={status!r}"
            f")"
        )