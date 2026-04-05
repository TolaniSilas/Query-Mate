"""
this is the main orchestrator. it wires or connects all agents together into a single call.

full flow logic or idea:
    question: Qustion from Users or Client
    --> [SQL Agent]: collects natural language (NL) and returns SQL (with retry loop)

    --> Validator Gate: 
        --> [Validator Agent]: quality + intent check for generated SQL query (runs inside sql agent loop); this is solely to
            confirm if the generated SQL command could execute or fulfils the user question and satifsy the DB.
        --> [query_validator]: security check (SELECT-only enforcement). It enforces ONLY 'SELECT' statements to 
            execute, all other statement command won't run.

    --> [executor]: run the validated SQL query on DB.

    --> [Response Agent]: return results in natural language.

    
    see the readme for the system design or achitecture diagram.
"""


from querymate.core.logger import get_logger
from querymate.agents.sql_agent import run_sql_agent
from querymate.agents.validator_agent import validator_agent
from querymate.agents.response_agent import generate_response
from querymate.core.connection import execute_query
from querymate.core.query_validator import is_safe_query
from querymate.security.guardrails import validate_question, GuardrailViolation



logger = get_logger(__name__)


def run_pipeline(question: str, schema_prompt: str, db_type: str, session_id: str) -> dict:
    """
    run the full multi-step agent pipeline.

    params
        question: user's natural language question
        schema_prompt: CREATE TABLE-style schema string from schema_inspector
        db_type: "sqlite" | "postgresql" | "mysql"
        session_id: active session id for query execution

    returns
        {
            "answer": str,     
            "sql": str | None, 
            "rows": list | None,
            "row_count": int,
            "truncated": bool,  
            "attempts": int,
            "status": str, 
            "error": str | None,
        }
    """

    logger.info("pipeline | starting | question: %s", question)

    try:
        question = validate_question(question)
        
    except GuardrailViolation as e:
        logger.warning("pipeline | guardrail violation | reason: %s", str(e))
        return {
            "answer": str(e),
            "sql": None,
            "rows": None,
            "row_count": 0,
            "truncated": False,
            "attempts": 0,
            "status": "guardrail_violation",
            "error": str(e),
        }
    
    except ValueError as e:
        logger.warning("pipeline | invalid question | reason: %s", str(e))
        return {
            "answer": str(e),
            "sql": None,
            "rows": None,
            "row_count": 0,
            "truncated": False,
            "attempts": 0,
            "status": "error",
            "error": str(e),
        }
    

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

        return execute_query(sql, session_id)

    sql_result = run_sql_agent(
        question = question,
        schema_prompt = schema_prompt,
        db_type = db_type,
        validator_fn = lambda q, s, sp: validator_agent(q, s, sp),
        executor_fn = safe_executor,
    )

    if sql_result["status"] == "ok" and "SECURITY_REJECTED" in str(sql_result.get("error", "")):
        sql_result["status"] = "security_rejected"

    logger.info("pipeline | sql_result status: %s | attempts: %s", sql_result["status"], sql_result.get("attempts"))

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