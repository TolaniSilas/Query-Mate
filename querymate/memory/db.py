import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from querymate.core.logger import get_logger


logger = get_logger(__name__)

_memory_engine = None
_SessionLocal = None


def get_memory_engine():
    global _memory_engine
    if _memory_engine is None:
        memory_database_url = os.environ.get("MEMORY_DATABASE_URL")
        if not memory_database_url:
            raise RuntimeError(
                "MEMORY_DATABASE_URL is not set. "
                "Add it to your .env to enable conversation memory."
            )
        
        _memory_engine = create_engine(memory_database_url, pool_pre_ping=True)

        logger.info("memory | engine initialised")
    
    return _memory_engine


def get_memory_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_memory_engine())

    return _SessionLocal()
