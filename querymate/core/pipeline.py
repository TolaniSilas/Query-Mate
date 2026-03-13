"""
this is the main orchestrator. it wires all agents together into a single call.

full flow:
    question
    --> [SQL Agent]         NL --> SQL (with retry loop)
        --> [Validator Agent]   quality + intent check (runs inside sql agent loop)
    --> [query_validator]   security check (SELECT-only enforcement)
    --> [executor]          run SQL on DB
    --> [Response Agent]    results --> natural language answer
"""


from core.logger import get_logger
from agents.sql_agent import run_sql_agent
from agents.validator_agent import validator_agent
from agents.response_agent import generate_response
from core.connection import execute_query
from core.query_validator import is_safe_query



logger = get_logger(__name__)


def run_pipeline(question: str, schema_prompt: str, db_type: str, session_id: str) -> dict:
    """
    runs the full natural language --> SQL --> validate --> execute --> respond pipeline.

    parameters
    ----------
    question      : user's natural language question
    schema_prompt : CREATE TABLE-style schema string from schema_inspector
    db_type       : "sqlite" | "postgresql" | "mysql"
    session_id    : active session id for query execution

    returns
    -------
    {
        "answer":    str,        # natural language answer shown to the user
        "sql":       str | None, # the SQL that was generated and executed
        "rows":      list | None,# raw result rows (for UI table display)
        "row_count": int,
        "truncated": bool,       # True if rows were capped for LLM
        "attempts":  int,        # how many SQL generation attempts were made
        "status":    str,        # "ok" | "cannot_answer" | "security_rejected" | ...
        "error":     str | None,
    }
    """

    logger.info("pipeline | starting | question: %s", question)

    def safe_executor(sql: str) -> dict:
        """
        security gate for rejecting anything that isn't a SELECT before hitting the DB.
        this idea is intentionally separate or different from the Validator Agent (which is quality for query validation, not security).
        this safe executor is for security check.
        """

        safe, reason = is_safe_query(sql)
        if not safe:
            logger.warning("pipeline | security_rejected | reason: %s", reason)
            return {
                "rows": None,
                "error": f"SECURITY_REJECTED: {reason}"
            }

        # query is safe - execute on the actual database.
        return execute_query(sql, session_id)

    # run the SQL Agent (includes Validator Agent retry loop).
    sql_result = run_sql_agent(
        question = question,
        schema_prompt = schema_prompt,
        db_type = db_type,
        validator_fn = lambda q, s, sp: validator_agent(q, s, sp),
        executor_fn = safe_executor,
    )

    # surface security rejections clearly in the status.
    if sql_result["status"] == "ok" and "SECURITY_REJECTED" in str(sql_result.get("error", "")):
        sql_result["status"] = "security_rejected"

    logger.info("pipeline | sql_result status: %s | attempts: %s", sql_result["status"], sql_result.get("attempts"))

    # pass everything to the Response Agent.
    response = generate_response(
        question = question,
        sql = sql_result.get("sql") or "",
        rows = sql_result.get("rows"),
        status = sql_result["status"],
        error = sql_result.get("error"),
        attempts = sql_result.get("attempts", 1),
    )

    logger.info("pipeline | completed | status: %s", response["status"])

    return {
        "answer": response["answer"],
        "sql": sql_result.get("sql"),
        "rows": sql_result.get("rows"),
        "row_count": response["row_count"],
        "truncated": response["truncated"],
        "attempts": sql_result.get("attempts", 1),
        "status": response["status"],
        "error": sql_result.get("error"),
    }