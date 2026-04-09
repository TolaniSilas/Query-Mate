"""
builds a conversation context string from recent message history.
the output is injected into both the SQL agent and Response agent prompts.

strategy:
    short sessions (≤ 6 messages / 3 exchanges) — all messages formatted verbatim.
    long sessions (> 6 messages) — split:
        older half: LLM-compressed summary (preserves intent, tables, filters, patterns)
        recent 4: kept verbatim (to carry follow-up references)
"""

from querymate.memory.store import get_recent_messages
from querymate.core.llm import chat
from querymate.core.logger import get_logger


logger = get_logger(__name__)

# sessions with more than this many messages trigger LLM compression
COMPRESSION_THRESHOLD = 15


_COMPRESS_SYSTEM_PROMPT = """You are a memory compression assistant for an analytics query system called QueryMate.

    Your job is to compress a partial conversation transcript into a dense, information-rich summary that another
    AI agent can use to accurately answer follow-up questions. The agent reading your summary has no other access
    to the original conversation — your summary is its only memory.

    WHAT TO PRESERVE — retain every piece of information that could affect a future SQL query or response:
    - The user's analytical intent and what business question they are exploring
    - Every data domain touched: which entities were discussed
    - Every filter, condition, or constraint the user specified (date ranges, statuses, thresholds, regions, etc.)
    - Every aggregation pattern used: totals, averages, top-N, comparisons, growth rates
    - Key numbers, values, or facts that came up in answers (e.g. "top merchant had $1.2M revenue")
    - Any follow-up patterns: refinements, drill-downs, or pivots the user made
    - Questions that were already fully answered (so they are not re-explained unnecessarily)
    - Any question that could NOT be answered and why

    WHAT TO OMIT:
    - Raw SQL syntax (describe what it did, not the code itself)
    - Verbose row-by-row data — only keep aggregate insights
    - Filler, greetings, or conversational padding

    FORMAT:
    Write flowing prose, 3-6 sentences maximum. Be dense and specific. Every sentence should carry facts.
    Do not use bullet points, headers, or structure — pure prose only.
"""


_COMPRESS_USER_PROMPT = """Compress the following conversation excerpt into a dense summary.
    Preserve all analytical intent, filters, data domains, and key findings — these will be used
    to answer follow-up questions.

    Conversation excerpt:
    {transcript}

    Compressed summary:
"""


def _format_message_block(messages: list[dict]) -> str:
    """
    formats a list of message dicts into a readable transcript block.
    """

    lines = []
    for msg in messages:
        if msg["role"] == "user":
            lines.append(f"User asked: {msg['content']}")

        else:
            lines.append(f"Assistant answered: {msg['content']}")
            if msg["sql"]:
                lines.append(f"SQL used: {msg['sql']}")
        lines.append("")

    return "\n".join(lines).strip()


def _compress(messages: list[dict]) -> str:
    """
    calls the LLM to compress a list of older messages into a summary paragraph.
    falls back to verbatim formatting if the LLM call fails — never breaks the pipeline.
    """

    transcript = _format_message_block(messages)
    try:
        summary = chat(
            system=_COMPRESS_SYSTEM_PROMPT,
            user=_COMPRESS_USER_PROMPT.format(transcript=transcript),
            max_tokens=512,
            provider="anthropic",
            model="claude-haiku-4-5-20251001",
        )

        logger.debug("context | compressed %d messages into summary", len(messages))

        return summary.strip()
    
    except Exception as e:
        logger.warning("context | compression failed, falling back to verbatim | error: %s", str(e))

        return transcript


def build_context(session_id: str) -> str | None:
    """
    retrieves recent messages for the session and builds a prompt-ready context block.

    for short sessions: all messages formatted verbatim.
    for long sessions: older messages are LLM-compressed, last 4 kept verbatim.

    returns None if there is no history yet (first question in session).
    """

    messages = get_recent_messages(session_id)

    if not messages:
        return None

    if len(messages) <= COMPRESSION_THRESHOLD:
        history_block = _format_message_block(messages)
        logger.debug("context | verbatim context from %d messages for session: %s", len(messages), session_id)

    else:
        older = messages[:-4]
        recent = messages[-4:]

        compressed_summary = _compress(older)
        verbatim_block = _format_message_block(recent)

        history_block = (
            f"[SUMMARY OF EARLIER CONVERSATION]\n{compressed_summary}"
            f"\n\n[RECENT EXCHANGES — verbatim]\n{verbatim_block}"
        )

        logger.debug("context | compressed %d older + verbatim %d recent messages for session: %s", len(older), len(recent), session_id)


    return f"""CONVERSATION HISTORY — the user has already asked the following questions in this session.
        Use this context to:
        - Resolve follow-up references ("those", "them", "the same", "filter further", "now show me...")
        - Understand the user's ongoing analytical intent and what they are trying to investigate
        - Avoid re-explaining facts already established in prior answers
        - Build on prior SQL patterns when the user is drilling down or refining

        {history_block}
    """