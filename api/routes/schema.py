"""
this helps to returns the cached schema for an active session.

    GET  /api/schema?session_id=xxx  --> full schema dict + prompt
"""

from fastapi import APIRouter
from api.schemas.models import SchemaResponse
from querymate.core.connection import get_session
from querymate.core.logger import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.get("/schema", response_model=SchemaResponse)
def get_schema(session_id: str):
    """
    returns the full schema dict and the CREATE TABLE prompt for the
    connected database. useful for debugging and building the frontend
    schema viewer.
    """
    session = get_session(session_id)

    if not session:
        logger.warning("api | schema | session not found: %s", session_id)
        return SchemaResponse(
            status = "error",
            db_type = None,
            tables = None,
            prompt = None,
            error = "Session not found. Please reconnect to the database.",
        )

    return SchemaResponse(
        status = "ok",
        db_type = session["db_type"],
        tables = session["schema"]["tables"],
        prompt = session["schema_prompt"],
        error = None,
    )