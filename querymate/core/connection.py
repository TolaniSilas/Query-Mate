"""
database connection manager for SQLite, PostgreSQL, and MySQL.

responsibilities:
  - build and validate connections for all three supported DB types
  - cache the active engine + schema per session (inspect once, reuse always)
  - enforce read-only access at the connection level for secure DB purposes.
  - execute queries safely and return serialisable results
  - clean up connections on disconnect

read-only enforcement strategy (layered):
  SQLite -> connect with uri=True + mode=ro flag
  PostgreSQL -> SET TRANSACTION READ ONLY on every connection checkout
  MySQL -> SET SESSION TRANSACTION READ ONLY on connect
  All -> query_validator.py rejects non-SELECT before execution (belt + braces)
"""


import os
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from typing import Any
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from querymate.core.schema_inspector import get_schema_and_prompt
from querymate.core.logger import get_logger


logger = get_logger(__name__)


# in-memory session store — keyed by session_id.
# holds engine, schema dict, and prompt string per session.
# in production, replace with Redis or a proper session backend.
_sessions: dict[str, dict] = {}



def _build_sqlite_engine(database: str) -> Engine:
    """
    enforce read-only at the SQLite URI level.
    """

    uri    = f"file:{database}?mode=ro"
    engine = create_engine(
        f"sqlite:///{database}",
        connect_args={"uri": True, "database": uri},
    )
    return engine



def _build_url_engine(url: str, db_type: str) -> Engine:
    """
    builds an engine directly from DATABASE_URL for postgresql and mysql.
    SQLAlchemy handles all query params — sslmode, channel_binding, etc.
    """

    engine = create_engine(url, pool_pre_ping=True)

    @event.listens_for(engine, "connect")
    def set_read_only(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        if db_type == "postgresql":
            cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        else:
            cursor.execute("SET SESSION TRANSACTION READ ONLY")
        cursor.close()

    return engine



def connect(session_id: str, db_type: str, credentials: dict) -> dict:
    """
    establishes a DB connection, inspects the schema, and caches everything under the given session_id.

    params
        session_id: unique identifier for this user session
        db_type: "sqlite" | "postgresql" | "mysql"
        credentials: dict of connection parameters

            SQLite:{ "database": "/path/to/file.db" }
            PostgreSQL / MySQL: { "url": "DATABASE_URL" }

    returns
        {
            "status": "ok" | "error",
            "db_type": str,
            "table_count": int,
            "tables": [str, ...],
            "error": str | None
        }
    """

    try:
        db_type = db_type.lower()

        logger.info("connection | connecting | db_type: %s | session: %s", db_type, session_id)

        if db_type == "sqlite":
            engine = _build_sqlite_engine(credentials["database"])
            connection_string = f"sqlite:///{credentials['database']}"

        elif db_type in ("postgresql", "mysql"):
            engine = _build_url_engine(credentials["url"], db_type)
            connection_string = credentials["url"]

        else:
            logger.warning("connection | unsupported db_type: %s", db_type)
            return {"status": "error", "error": f"Unsupported database type: '{db_type}'."}

        # test the connection before caching
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # inspect schema once and cache everything for the session
        schema, schema_prompt = get_schema_and_prompt(connection_string)
        tables = list(schema["tables"].keys())

        _sessions[session_id] = {
            "engine": engine,
            "db_type": db_type,
            "schema": schema,
            "schema_prompt": schema_prompt,
        }

        logger.info("connection | connected | tables: %d | session: %s", len(tables), session_id)

        return {
            "status": "ok",
            "db_type": db_type,
            "table_count": len(tables),
            "tables": tables,
            "error": None,
        }

    except Exception as e:
        logger.error("connection | failed to connect | session: %s | error: %s", session_id, str(e), exc_info=True)
        return {"status": "error", "error": str(e)} 



def disconnect(session_id: str) -> dict:
    """
    disposes the engine and removes the session from cache.
    """

    if session_id not in _sessions:
        logger.warning("connection | disconnect | session not found: %s", session_id)

        return {"status": "error", "error": "Session not found."}

    try:
        _sessions[session_id]["engine"].dispose()
        del _sessions[session_id]
        logger.info("connection | disconnected | session: %s", session_id)

        return {"status": "ok", "error": None}

    except Exception as e:
        logger.error("connection | disconnect error | session: %s | error: %s", session_id, str(e), exc_info=True)

        return {"status": "error", "error": str(e)}



def get_session(session_id: str) -> dict | None:
    """
    returns the cached session dict for the given session_id, or None.
    """
    return _sessions.get(session_id)



def execute_query(sql: str, session_id: str) -> dict:
    """
    executes a SQL query on the session's cached engine.

    params
        sql: a validated SELECT query
        session_id: the active session

    returns
        {
            "rows": list[dict] | None,
            "columns": list[str] | None,
            "error": str | None
        }
    """
    
    session = get_session(session_id)

    if not session:
        logger.warning("connection | execute_query | no active session: %s", session_id)
        return {"rows": None, "columns": None, "error": "No active database session found."}

    try:
        logger.debug("connection | executing query | session: %s\n%s", session_id, sql)

        with session["engine"].connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [
                {col: _serialize(val) for col, val in zip(columns, row)}
                for row in result.fetchall()
            ]

        logger.info("connection | query executed | rows returned: %d", len(rows))
        return {"rows": rows, "columns": columns, "error": None}

    except Exception as e:
        logger.error("connection | query execution error: %s", str(e), exc_info=True)
        return {"rows": None, "columns": None, "error": str(e)}




# internal helpers function.
def _serialize(value: Any) -> Any:
    """
    converts non-JSON-serialisable DB types to plain Python types.
    """

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    return value





# if __name__ == "__main__":

#     import os
#     from dotenv import load_dotenv
#     import sys
#     from core.query_validator import is_safe_query

#     load_dotenv()

#     SESSION_ID = "test-session-123"

#     # connect to a database.
#     print("connecting...")
#     conn_result = connect(
#         session_id = SESSION_ID,
#         db_type = "postgresql",
#         credentials = {"url": os.environ["DATABASE_URL"]},
#     )

#     print()
#     print(f"status: {conn_result['status']}")
#     print(f"table_count: {conn_result['table_count']}")
#     print(f"tables: {conn_result['tables']}")
#     print(f"error: {conn_result['error']}")
#     print()
#     print()

#     if conn_result["status"] != "ok":
#         print("connection failed — aborting.")
#         sys.exit(1)
    

#     # execute query.
#     print("executing query...")
#     sql = """
#         SELECT merchant_id, SUM(amount) AS total
#         FROM merchant_activities
#         WHERE status = 'SUCCESS'
#         GROUP BY merchant_id
#         ORDER BY SUM(amount) DESC
#         LIMIT 1
#     """


#     def safe_executor(sql: str) -> dict:
#         """
#         security gate for rejecting anything that isn't a SELECT before hitting the DB.
#         this idea is intentionally separate or different from the Validator Agent (which is quality for query validation, not security).
#         this safe executor is for security check.
#         """

#         safe, reason = is_safe_query(sql)
#         if not safe:
#             logger.warning("pipeline | security_rejected | reason: %s", reason)
#             return {
#                 "rows": None,
#                 "error": f"SECURITY_REJECTED: {reason}"
#             }

#         # query is safe - execute on the actual database.
#         return execute_query(sql, SESSION_ID)
    
    
#     exe_query = safe_executor(sql)

#     if exe_query["error"]:
#         print(f"error: {exe_query['error']}")
#         print(f"rows: {exe_query['rows']}")
        
#     else:
#         print()
#         print(f"columns: {exe_query['columns']}")
#         print(f"rows: {exe_query['rows']}")
#         print(f"error: {exe_query['error']}")
#         print()
#         print()


#     # disconnect from the databse.
#     print("disconnecting...")
#     disc_result = disconnect(SESSION_ID)
#     print()
#     print(f"status: {disc_result['status']}")