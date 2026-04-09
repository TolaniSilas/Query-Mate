"""
SQLAlchemy ORM models for QueryMate's internal memory store.

Tables:
    qm_users: one record per unique user_id passed into QueryMate
    qm_sessions: one record per QueryMate instantiation (one active per user at a time)
    qm_messages: every question and answer, linked to a session

Constraints:
    partial unique index on qm_sessions(user_id) WHERE is_active = TRUE
    enforces the one-active-session-per-user rule at the database level.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, relationship
from querymate.core.logger import get_logger
from querymate.memory.db import get_memory_engine


logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "qm_users"

    user_id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sessions = relationship("MemorySession", back_populates="user")


class MemorySession(Base):
    __tablename__ = "qm_sessions"

    __table_args__ = (
        Index(
            "uq_one_active_session_per_user",
            "user_id",
            unique=True,
            postgresql_where=Column("is_active") == True,
        ),
    )

    session_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("qm_users.user_id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "qm_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("qm_sessions.session_id"), nullable=False)
    role = Column(String, nullable=False) 
    content = Column(Text, nullable=False)    
    sql = Column(Text, nullable=True)  
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("MemorySession", back_populates="messages")


def create_tables() -> None:
    """
    creates all QueryMate memory tables if they don't already exist.
    """
    Base.metadata.create_all(get_memory_engine())

    logger.info("memory | tables verified or created")
