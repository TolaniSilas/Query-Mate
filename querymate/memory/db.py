import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from querymate.core.logger import get_logger


logger = get_logger(__name__)

_memory_engine = None
_SessionLocal = None


def get_memory_engine():
    global _memory_engine
    if _memory_engine is None:
        url = os.environ.get("MEMORY_DATABASE_URL")
        if not url:
            raise RuntimeError(
                "MEMORY_DATABASE_URL is not set. "
                "Add it to your .env to enable conversation memory."
            )

        try:
            engine = create_engine(url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            _memory_engine = engine
            logger.info("memory | engine initialised")

        except OperationalError as e:
            raise ConnectionError(
                f"QueryMate could not connect to the memory database.\n"
                f"Check that MEMORY_DATABASE_URL in your .env is correct and the database is reachable.\n"
                f"Current value: {url}\n"
                f"Error: {e.orig}"
            ) from e

    return _memory_engine


def get_memory_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_memory_engine())

    return _SessionLocal()