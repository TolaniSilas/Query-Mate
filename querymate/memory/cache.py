import os
import json
import redis
from querymate.core.logger import get_logger


logger = get_logger(__name__)

_redis_client = None

# sessions expire from Redis after 24 hours of inactivity
SESSION_TTL = 86_400


def _get_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        url = os.environ.get("REDIS_URL")
        if not url:
            raise RuntimeError(
                "REDIS_URL is not set. "
                "Add it to your .env to enable session caching."
            )
        
        _redis_client = redis.from_url(url, decode_responses=True)

        logger.info("memory | redis client initialised")
    
    return _redis_client


def _key(session_id: str) -> str:
    return f"qm:session:{session_id}"


def set_session_cache(session_id: str, data: dict) -> None:
    """
    stores serialisable session metadata in Redis with a TTL.
    data should contain: db_type, schema_prompt, connection_string
    """

    _get_client().setex(_key(session_id), SESSION_TTL, json.dumps(data))
    logger.debug("cache | session stored: %s", session_id)


def get_session_cache(session_id: str) -> dict | None:
    """
    retrieves session metadata from Redis.
    returns None if not found or expired.
    """

    raw = _get_client().get(_key(session_id))
    return json.loads(raw) if raw else None


def delete_session_cache(session_id: str) -> None:
    """
    removes a session from Redis on disconnect.
    """
    
    _get_client().delete(_key(session_id))
    logger.debug("cache | session deleted: %s", session_id)