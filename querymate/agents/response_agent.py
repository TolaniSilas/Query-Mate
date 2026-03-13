"""
this agent takes raw sql query results and converts them into a natural language answer.
the LLM synthesises the data into insight - never lists rows or exposes sql.
"""

import json
from core.llm import chat
from core.logger import get_logger


logger = get_logger(__name__)

# cap how many rows we send to the LLM to avoid blowing the context window.
max_rows_to_llm = 50


def _build_system_prompt() -> str:
    return """You are a knowledgeable and articulate data analyst assistant embedded in a business intelligence tool.
Your role is to interpret database query results and communicate findings in clear, natural, conversational English — the way a senior analyst would explain data to a business stakeholder in a meeting.

CRITICAL RULES — never break these:
- NEVER list rows, bullet points, or enumerate records one by one. Not even partially.
- NEVER output tables, grids, or structured data of any kind.
- NEVER say "Row 1 shows...", "The first record is...", or anything that references individual rows.
- NEVER expose SQL, column names, table names, or any technical database internals in your response.
- NEVER start your response with "Based on the query results" or "The data shows" — get straight to the answer.

HOW TO RESPOND:
- Answer the question directly in the first sentence, as if you already know the answer.
- Speak in flowing, natural prose — like a confident analyst giving a verbal briefing.
- Synthesise the data into insight: totals, trends, comparisons, highs, lows, notable patterns.
- If there is only one result, state it naturally and add brief context where useful.
- If there are multiple results, summarise what they collectively tell us — not what each one says individually.
- If the result set is empty, say so plainly and offer a likely reason in plain language.
- Keep it concise. One to three sentences is often enough. Only go longer if the data genuinely warrants it.

TONE: Confident, clear, professional but approachable. No jargon. No hedging. No filler phrases.
"""


def _build_results_summary(rows: list, row_count: int, truncated: bool) -> str:
    """
    summarise the shape and content of results and not a raw JSON dump.
    this nudges the LLM toward synthesis rather than listing.
    """

    if row_count == 0:
        return "The query returned no results."

    rows_for_llm = rows[:max_rows_to_llm]
    columns = list(rows_for_llm[0].keys()) if rows_for_llm else []

    summary_lines = [
        f"Total records returned: {row_count}"
        + (" (summarise from the first 50 shown below)" if truncated else ""),
        f"Fields available: {', '.join(columns)}",
        "",
        "Data:",
        json.dumps(rows_for_llm, indent=2, default=str),
    ]

    return "\n".join(summary_lines)


def generate_response(question: str, sql: str, rows: list | None, status: str, 
                      error: str | None = None, attempts: int = 1
                      ) -> dict:

    # non-ok statuses - no LLM call needed.
    if status == "cannot_answer":
        logger.info("response_agent | cannot_answer | question: %s", question)
        return {
            "answer": "That question doesn't appear to match anything in the connected database. "
                         "The information may not exist in the available data, or the question may need "
                         "to be rephrased to match what's stored.",
            "row_count": 0,
            "truncated": False,
            "status": status,
        }

    if status in ("validation_failed", "error"):
        logger.warning("response_agent | pipeline failed | status: %s | error: %s", status, error)
        return {
            "answer": f"Something went wrong while trying to answer your question after {attempts} attempt(s). "
            "Please try rephrasing it, or contact your administrator if the problem persists.",
            "row_count": 0,
            "truncated": False,
            "status": status,
        }

    # prepare results.
    row_count = len(rows) if rows else 0
    truncated = row_count > max_rows_to_llm
    results_summary = _build_results_summary(rows or [], row_count, truncated)

    logger.info("response_agent | generating response | row_count: %d | truncated: %s", row_count, truncated)

    user_content = (
        f"Question asked: {question}\n\n"
        f"Query results:\n{results_summary}\n\n"
        f"Answer the question in natural language. Do not list or enumerate the records."
    )

    try:
        answer = chat(
            system = _build_system_prompt(),
            user = user_content,
            max_tokens = 1024,
            provider = "anthropic",
            model = "claude-sonnet-4-20250514",
        )

        logger.debug("response_agent | answer generated successfully")

        return {
            "answer": answer,
            "row_count": row_count,
            "truncated": truncated,
            "status": "ok",
        }

    except Exception as e:
        logger.error("response_agent | API error during response generation: %s", str(e), exc_info=True)
        return {
            "answer": "The data was retrieved but I ran into an issue composing the response. "
            f"The query returned {row_count} result(s).",
            "row_count": row_count,
            "truncated": truncated,
            "status": "error",
        }