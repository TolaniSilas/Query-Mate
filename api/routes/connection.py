"""
handles database connection and disconnection.

    POST /api/connect --> establish DB connection, return session_id
    DELETE /api/disconnect --> tear down connection, wipe session
"""

import uuid
from fastapi import APIRouter
from api.schemas.models import ConnectRequest, ConnectResponse, DisconnectResponse
from querymate.core.connection import connect, disconnect
from querymate.core.logger import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.post("/connect", response_model=ConnectResponse)
def connect_to_database(request: ConnectRequest):
    """
    accepts DB credentials from the frontend, opens a read-only connection,
    inspects the schema, and returns a session_id.

    the frontend stores the session_id and sends it with every subsequent request.
    credentials are held server-side only — never returned to the frontend.
    """
    
    db_type = request.db_type.lower().strip()

    # build credentials from the request
    if db_type == "sqlite":
        if not request.sqlite_path:
            return ConnectResponse(
                status = "error",
                session_id = None,
                db_type = db_type,
                table_count = None,
                tables = None,
                error = "sqlite_path is required for db_type='sqlite'.",
            )
        credentials = {"database": request.sqlite_path}

    elif db_type in ("postgresql", "mysql"):
        if not request.database_url:
            return ConnectResponse(
                status = "error",
                session_id = None,
                db_type = db_type,
                table_count = None,
                tables = None,
                error = "database_url is required for postgresql and mysql.",
            )
        credentials = {"url": request.database_url}

    else:
        return ConnectResponse(
            status = "error",
            session_id = None,
            db_type = db_type,
            table_count = None,
            tables = None,
            error = f"Unsupported db_type: '{db_type}'. Choose from: postgresql, mysql, sqlite.",
        )

    session_id = str(uuid.uuid4())

    logger.info("api | connect | db_type: %s | session: %s", db_type, session_id)

    result = connect(
        session_id = session_id,
        db_type = db_type,
        credentials = credentials,
    )

    if result["status"] != "ok":
        return ConnectResponse(
            status = "error",
            session_id = None,
            db_type = db_type,
            table_count = None,
            tables = None,
            error = result["error"],
        )

    return ConnectResponse(
        status = "ok",
        session_id = session_id,
        db_type = result["db_type"],
        table_count = result["table_count"],
        tables = result["tables"],
        error = None,
    )


@router.delete("/disconnect", response_model=DisconnectResponse)
def disconnect_from_database(session_id:str):
    """
    tears down the DB connection and wipes all session data.
    """

    logger.info("api | disconnect | session: %s", session_id)

    result = disconnect(session_id)

    return DisconnectResponse(
        status = result["status"],
        error = result.get("error"),
    )