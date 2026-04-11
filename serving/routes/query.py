"""
the main query endpoint - receives a natural language question,
runs the full pipeline, and returns the answer.

    POST  /api/query  --> NL question --> SQL --> execute --> NL answer
"""

from fastapi import APIRouter
from serving.schemas.models import QueryRequest, QueryResponse
from querymate.core.connection import get_session
from querymate.core.pipeline import run_pipeline
from querymate.core.logger import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.post("/query", response_model=QueryResponse)
def query_database(request: QueryRequest):
    """
    accepts a natural language question and session_id.
    runs the full agent pipeline:
        --> SQL Agent --> Validator Agent --> security check --> execute --> Response Agent
    returns the natural language answer + generated SQL + raw rows.
    """
    session = get_session(request.session_id)

    if not session:
        logger.warning("serving | query | session not found: %s", request.session_id)
        return QueryResponse(
            status = "error",
            answer = None,
            sql = None,
            rows = None,
            row_count = None,
            truncated = None,
            attempts = None,
            error = "Session not found. Please reconnect to the database.",
        )

    logger.info("serving | query | session: %s | question: %s", request.session_id, request.question)

    result = run_pipeline(question = request.question, 
                          schema_prompt = session["schema_prompt"], 
                          db_type = session["db_type"], 
                          session_id = request.session_id
                          )

    return QueryResponse(
        status = result["status"],
        answer = result["answer"],
        sql = result["sql"],
        rows = result["rows"],
        row_count = result["row_count"],
        truncated = result["truncated"],
        attempts = result["attempts"],
        error = result["error"],
    )