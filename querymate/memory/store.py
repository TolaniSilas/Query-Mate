"""
CRUD operations for QueryMate's memory store.

all reads and writes to qm_users, qm_sessions, qm_messages go through here.
"""

import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from querymate.memory.db import get_memory_session
from querymate.memory.models import User, MemorySession, Message
from querymate.core.logger import get_logger


logger = get_logger(__name__)

# number of recent messages to retrieve for context injection.
CONTEXT_WINDOW = 50


@contextmanager
def _session():
    """
    context manager that auto-commits on success and rolls back on error.
    """

    s = get_memory_session()

    try:
        yield s

    except Exception:
        s.rollback()
        raise

    else: 
        s.commit()

    finally:
        s.close()



def ensure_user(user_id: str) -> None:
    """
    upserts the user record. silent no-op if the user already exists.
    """

    with _session() as s:
        if not s.get(User, user_id):
            s.add(User(user_id=user_id))

    logger.info("memory | user ensured: %s", user_id)



def close_active_session(user_id: str) -> None:
    """
    marks any currently active session for this user as ended.
    enforces the one-active-session-per-user constraint.
    """

    with _session() as s:
        active = (s.query(MemorySession)
            .filter_by(user_id=user_id, is_active=True)
            .first()
        )
        if active:
            active.is_active = False
            active.ended_at = datetime.now(timezone.utc)

            logger.info("memory | closed previous session: %s for user: %s", active.session_id, user_id)



def create_session(user_id: str, session_id: str) -> None:
    """
    opens a new active memory session for the user.
    always call close_active_session() first.
    """

    with _session() as s:
        s.add(MemorySession(session_id=session_id, user_id=user_id, is_active=True))

    logger.info("memory | session created: %s for user: %s", session_id, user_id)



def end_session(session_id: str) -> None:
    """
    marks a session as ended. called on disconnect.
    """

    with _session() as s:
        mem_session = s.get(MemorySession, session_id)
        if mem_session:
            mem_session.is_active = False
            mem_session.ended_at = datetime.now(timezone.utc)

    logger.info("memory | session ended: %s", session_id)



def save_message(session_id: str, role: str, content: str, sql: str | None = None) -> None:
    """
    persists a single message to the store.

    params
        session_id: the active memory session
        role: "user" | "assistant"
        content: the question or the natural language answer
        sql: the generated SQL (assistant messages only)
    """

    with _session() as s:
        s.add(Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            sql=sql,
        ))



def get_recent_messages(session_id: str, limit: int = CONTEXT_WINDOW) -> list[dict]:
    """
    retrieves the most recent messages for a session, returned in chronological order.

    returns
        list of dicts: [{role, content, sql}, ...]
    """

    with _session() as s:
        messages = (
            s.query(Message)
            .filter_by(session_id=session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {"role": m.role, "content": m.content, "sql": m.sql}
            for m in reversed(messages)
        ]