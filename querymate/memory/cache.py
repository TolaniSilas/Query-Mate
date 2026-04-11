import os
import json
import redis
from redis.exceptions import ConnectionError as RedisConnectionError
from querymate.core.logger import get_logger


logger = get_logger(__name__)

_redis_client = None
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

        try:
            client = redis.from_url(url, decode_responses=True)
            client.ping()
            _redis_client = client
            logger.info("memory | redis client initialised")

        except RedisConnectionError as e:
            raise ConnectionError(
                f"QueryMate could not connect to Redis.\n"
                f"Check that REDIS_URL in your .env is correct and Redis is reachable.\n"
                f"Current value: {url}\n"
                f"Error: {e}"
            ) from e

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
