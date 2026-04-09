"""
this converts a natural language question into a sql query using the LLM.
and accepts feedback from the validator agent and retries if needed.
"""

import re
from querymate.core.llm import chat
from querymate.core.logger import get_logger
from querymate.security.guardrails import INJECTION_GUARD


logger = get_logger(__name__)
max_retries = 3


def _build_system_prompt(schema_prompt: str, db_type: str, conversation_context: str | None = None) -> str:
    
    context_block = ""
    if conversation_context:
        context_block = f"""
    {conversation_context}

    Use the conversation history above to resolve follow-up references. If the current question
    refers to a previous result ("those", "them", "the same ones", "filter further"), build on
    the prior SQL rather than starting from scratch.
    """

    return f"""{INJECTION_GUARD}

    You are an expert {db_type.upper()} SQL query writer embedded in an intelligent Text-to-SQL system.

    This system serves non-technical business users — stakeholders, analysts, and executives — who interact
    with their relational databases using plain English. They have no SQL knowledge. Your job is to silently
    translate their intent into a precise, executable SQL query. The quality of their decision-making depends
    entirely on the accuracy of what you write.

    The database dialect is {db_type.upper()}. Write only syntax valid for this dialect.

    {schema_prompt}
    {context_block}
    YOUR TASK:
    Convert the user's natural language question into a single, correct, read-only SQL SELECT query.

    RULES — follow every one without exception:
    - Return ONLY the raw SQL query. No explanation, no markdown fences, no preamble, no trailing commentary.
    - Only write SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, TRUNCATE, or any DDL/DML.
    - Use the exact table and column names from the schema above — spelling and case must match exactly.
    - Use JOINs wherever the question requires data from more than one table. Base all joins on the
    foreign key relationships defined in the schema.
    - Apply filters (WHERE), aggregations (COUNT, SUM, AVG), groupings (GROUP BY), orderings (ORDER BY),
    and limits (LIMIT) only when the question clearly calls for them.
    - If the question is ambiguous, interpret it in the most reasonable and common-sense way for a
    business context.
    - If the question genuinely cannot be answered from the available schema — the data simply does not
    exist in any of the tables — respond with exactly: CANNOT_ANSWER

    ON RETRIES:
    If you receive feedback from a previous failed attempt, read it carefully and fix precisely what it
    describes. Do not rewrite the entire query — only correct the specific issue identified.
    """


def _extract_sql(raw: str) -> str:
    """
    strip markdown fences if the LLM wrapped it anyway.
    """

    cleaned = re.sub(r"```sql|```", "", raw, flags=re.IGNORECASE).strip()

    return cleaned


def generate_sql(question: str, schema_prompt: str, db_type: str, feedback: str | None = None, conversation_context: str | None = None) -> dict:
    """
    calls the LLM to generate a SQL query for the given question.

    params
        question: the user's natural language question
        schema_prompt : the CREATE TABLE-style schema string from schema_inspector
        db_type: "sqlite" | "postgresql" | "mysql"
        feedback: optional rejection reason from the Validator Agent (retry path)
        conversation_context: formatted history from context builder (optional)

    returns
        {
            "sql": str | None,
            "status": "ok" | "cannot_answer" | "error",
            "error": str | None
        }
    """

    system_prompt = _build_system_prompt(schema_prompt, db_type, conversation_context)

    # on a retry, append the validator's feedback so the LLM can self-correct
    user_content = question
    if feedback:
        logger.debug("sql_agent | retry with feedback: %s", feedback)
        user_content = (
            f"{question}\n\n"
            f"[Previous attempt was rejected. Feedback: {feedback}]\n"
            f"Please fix the SQL query based on this feedback."
        )

    try:
        raw_text = chat(
            system = system_prompt,
            user = user_content,
            max_tokens = 1024,
            provider = "anthropic",
            model = "claude-opus-4-6",
        )

        if "CANNOT_ANSWER" in raw_text.upper():
            logger.info("sql_agent | CANNOT_ANSWER | question: %s", question)
            return {
                "sql": None, 
                "status": "cannot_answer", 
                "error": None
                }

        sql = _extract_sql(raw_text)
        logger.debug("sql_agent | generated SQL:\n%s", sql)
        return {
            "sql": sql, 
            "status": "ok", 
            "error": None
            }

    except Exception as e:
        logger.error("sql_agent | API error during SQL generation: %s", str(e), exc_info=True)
        return {
            "sql": None, 
            "status": "error", 
            "error": str(e)
            }


def run_sql_agent(question: str, schema_prompt: str, db_type: str, validator_fn, executor_fn, conversation_context: str | None = None) -> dict:
    """
    orchestrates the sql generation in addition with the validation retry loop.

    design flow:
        generate SQL --> validate --> if rejected, regenerate with feedback --> repeat
        up to max_retries times before returning a failure.

    parameters
        question: user's natural language question
        schema_prompt: schema context string
        db_type: database dialect
        validator_fn: validator_agent.validate(question, sql, schema_prompt) -> dict
        executor_fn: executes SQL, returns {"rows": [...], "error": str | None}
        conversation_context: formatted history from context builder (optional)

    returns format
        {
            "sql": str | None,
            "rows": list | None,
            "status": "ok" | "cannot_answer" | "validation_failed" | "error",
            "attempts": int,
            "error": str | None,
        }
    """

    feedback = None
    last_error = None

    logger.info("sql_agent | starting pipeline | question: %s", question)

    for attempt in range(1, max_retries+1):

        logger.info("sql_agent | attempt %d of %d", attempt, max_retries)

        gen_result = generate_sql(question, schema_prompt, db_type, feedback, conversation_context)

        if gen_result["status"] == "cannot_answer":
            logger.info("sql_agent | question unanswerable from schema")
            return {
                "sql": None,
                "rows": None,
                "status": "cannot_answer",
                "attempts": attempt,
                "error": "Question cannot be answered from the available schema.",
            }

        if gen_result["status"] == "error":
            logger.error("sql_agent | generation error: %s", gen_result["error"])
            return {
                "sql": None,
                "rows": None,
                "status": "error",
                "attempts": attempt,
                "error": gen_result["error"],
            }

        sql = gen_result["sql"]

        # validate: quality + intent check (LLM-based)
        val_result = validator_fn(question, sql, schema_prompt)

        if val_result["status"] == "ok":
            exec_result = executor_fn(sql)

            if exec_result.get("error"):
                feedback = f"The SQL caused a database error: {exec_result['error']}"
                last_error = exec_result["error"]
                logger.warning("sql_agent | execution error on attempt %d: %s", attempt, last_error)
                continue

            logger.info("sql_agent | success on attempt %d | rows returned: %d", attempt, len(exec_result.get("rows") or []))
            
            return {
                "sql": sql,
                "rows": exec_result["rows"],
                "status": "ok",
                "attempts": attempt,
                "error": None,
            }

        # validation rejected; collect feedback for next attempt.
        feedback = val_result["feedback"]
        last_error = feedback
        logger.warning("sql_agent | validation rejected on attempt %d | feedback: %s", attempt, feedback)

    # exhausted all retries
    logger.error("sql_agent | all %d attempts exhausted | last error: %s", max_retries, last_error)
    return {
        "sql": sql,
        "rows": None,
        "status": "validation_failed",
        "attempts": max_retries,
        "error": f"Could not generate a valid query after {max_retries} attempts. Last issue: {last_error}",
    }