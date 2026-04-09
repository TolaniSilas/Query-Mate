"""
database connection manager for SQLite, PostgreSQL, and MySQL.

responsibilities:
    - build and validate connections for all three supported DB types
    - cache the active engine in-process + session metadata in Redis
    - enforce read-only access at the connection level for secure DB purposes.
    - execute queries safely and return serialisable results
    - clean up connections on disconnect

read-only enforcement strategy (layered):
    SQLite -> connect with uri=True + mode=ro flag
    PostgreSQL -> SET TRANSACTION READ ONLY on every connection checkout
    MySQL -> SET SESSION TRANSACTION READ ONLY on connect
    All -> query_validator.py rejects non-SELECT before execution (belt + braces)

session caching strategy:
    in-process dict (_engines) -> holds SQLAlchemy engine objects (not serialisable)
    Redis (cache.py) -> holds serialisable metadata (db_type, schema_prompt, connection_string). it aids to survives server restarts.
    get_session() checks _engines first, then Redis, rebuilding the engine on a miss.
"""


from decimal import Decimal
from datetime import datetime, date
from uuid import UUID
from typing import Any
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from querymate.core.schema_inspector import get_schema_and_prompt
from querymate.core.logger import get_logger
from querymate.memory.cache import set_session_cache, get_session_cache, delete_session_cache


logger = get_logger(__name__)


# in-process engine cache — keyed by session_id.
# engines cannot be serialised, so they always live here.
_engines: dict[str, Engine] = {}



def _build_sqlite_engine(database: str) -> Engine:
    """
    enforce read-only at the SQLite URI level.
    """

    uri = f"file:{database}?mode=ro"
    engine = create_engine(
        f"sqlite:///{database}",
        connect_args={"uri": True, "database": uri})

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
    establishes a DB connection, inspects the schema, and caches everything
    under the given session_id.

    params
        session_id: unique identifier for this user session
        db_type: "sqlite" | "postgresql" | "mysql"
        credentials: dict of connection parameters

            SQLite:{"database": "/path/to/file.db"}
            PostgreSQL / MySQL: {"url": "DATABASE_URL"}

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

        # test the connection before caching.
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # inspect schema once and cache everything for the session.
        schema, schema_prompt = get_schema_and_prompt(connection_string)
        tables = list(schema["tables"].keys())

        # engine stays in-process (not serialisable).
        _engines[session_id] = engine

        # serialisable metadata goes to Redis
        set_session_cache(session_id, {
            "db_type": db_type,
            "schema_prompt": schema_prompt,
            "connection_string": connection_string,
        })

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
    disposes the engine and removes the session from both in-process cache and Redis.
    """

    if session_id not in _engines:
        logger.warning("connection | disconnect | session not found: %s", session_id)
        return {"status": "error", "error": "Session not found."}

    try:
        _engines[session_id].dispose()
        del _engines[session_id]
        delete_session_cache(session_id)
        logger.info("connection | disconnected | session: %s", session_id)

        return {"status": "ok", "error": None}

    except Exception as e:
        logger.error("connection | disconnect error | session: %s | error: %s", session_id, str(e), exc_info=True)
        return {"status": "error", "error": str(e)}



def get_session(session_id: str) -> dict | None:
    """
    returns the full session dict for the given session_id, or None.

    fast path: engine is in _engines and metadata is in Redis.
    slow path (server restart): engine is gone but Redis still has metadata —
        rebuild the engine from the stored connection_string and re-cache it.
    """

    cached = get_session_cache(session_id)
    if not cached:
        return None

    if session_id in _engines:
        return {**cached, "engine": _engines[session_id]}

    # engine was lost; rebuild from Redis metadata.
    logger.info("connection | rebuilding engine from cache | session: %s", session_id)
    db_type = cached["db_type"]
    connection_string = cached["connection_string"]

    if db_type == "sqlite":
        engine = _build_sqlite_engine(connection_string.replace("sqlite:///", ""))

    else:
        engine = _build_url_engine(connection_string, db_type)

    _engines[session_id] = engine
    return {**cached, "engine": engine}



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