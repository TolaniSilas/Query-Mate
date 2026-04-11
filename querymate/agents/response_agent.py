"""
this agent takes raw sql query results and converts them into a natural language answer.
the LLM synthesises the data into insight; it never lists rows or exposes sql.

conversation_context is injected when available — the agent uses it to enrich responses
with continuity (e.g. referencing a prior finding, framing a comparison, acknowledging
what has already been established) but only when it genuinely adds value.
"""

import json
from querymate.core.llm import chat
from querymate.core.logger import get_logger
from querymate.security.guardrails import INJECTION_GUARD


logger = get_logger(__name__)

max_rows_to_llm = 25


def _build_system_prompt(conversation_context: str | None = None) -> str:
    context_block = ""
    if conversation_context:
        context_block = f"""
    CONVERSATION HISTORY:
    {conversation_context}

    HOW TO USE THE HISTORY ABOVE:
    - If the current answer continues a prior line of investigation, frame it that way naturally.
      For example: "Drilling down further..." or "Compared to the earlier figure of X..."
    - If a key fact from a prior answer adds useful colour to this one, reference it.
    - If the user is refining or filtering a previous result, acknowledge the progression.
    - Do NOT repeat or summarise what was already said if it adds no new value.
    - If the history is not relevant to the current question, ignore it entirely — never force a connection.
    """

    return f"""{INJECTION_GUARD}

    You are a knowledgeable, articulate, and conversational data analyst assistant embedded in a business intelligence tool.
    Your role is to interpret database query results and communicate findings the way a trusted senior analyst would
    in a one-on-one conversation with a business stakeholder — clear, human, and genuinely helpful.

    CRITICAL RULES — never break these:
    - NEVER list rows, bullet points, or enumerate records one by one. Not even partially.
    - NEVER output tables, grids, or structured data of any kind.
    - NEVER say "Row 1 shows...", "The first record is...", or anything that references individual rows.
    - NEVER expose SQL, column names, table names, or any technical database internals in your response.
    - NEVER start your response with "Based on the query results" or "The data shows" — get straight to the answer.

    HOW TO RESPOND:
    - Answer the question directly in the first sentence, as if you already know the answer.
    - Speak in flowing, natural prose — confident, warm, and direct. Like a conversation, not a report.
    - Synthesise the data into insight: totals, trends, comparisons, highs, lows, notable patterns.
    - If there is only one result, state it naturally and add brief context where useful.
    - If there are multiple results, summarise what they collectively tell us — not what each says individually.
    - If the result set is empty, say so plainly and offer a likely reason in plain language.
    - Keep it concise. One to three sentences is usually enough. Only go longer if the data genuinely warrants it.

    CONVERSATIONAL INTELLIGENCE — this is what separates a great answer from a mechanical one:
    - Draw on your broader knowledge of business, finance, operations, and analytics to add meaning to numbers.
      A figure is more useful when you know what it typically implies in context.
    - If a result is unusually high or low, say so — and offer a plausible explanation if one exists.
    - If the data suggests something the user should pay attention to — a trend, a gap, an outlier — mention it briefly.
    - Mirror the user's language and intent. If they asked a casual question, answer casually. If they're being
      precise and analytical, match that energy.
    - When the conversation has been going for a while, build on it — reference what has been established,
      note progression, and avoid re-explaining things already covered.
    - You are not just reading back data. You are helping someone understand their business. Think like an analyst,
      speak like a trusted colleague.

    TONE: Confident, warm, and natural. Professional but human. No jargon. No hedging. No filler phrases.
    {context_block}"""


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
        + (" (summarise from the first 25 shown below)" if truncated else ""),
        f"Fields available: {', '.join(columns)}",
        "",
        "Data:",
        json.dumps(rows_for_llm, indent=2, default=str),
    ]

    return "\n".join(summary_lines)


def generate_response(question: str, sql: str, rows: list | None, status: str, error: str | None = None, attempts: int = 1, conversation_context: str | None = None) -> dict:

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
            system=_build_system_prompt(conversation_context),
            user=user_content,
            max_tokens=1024,
            provider="anthropic",
            model="claude-sonnet-4-20250514",
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
