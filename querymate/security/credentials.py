import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

SUPPORTED_DB_TYPES = {"sqlite", "postgresql", "mysql"}


def get_db_credentials(db_type: str) -> dict:
    """
    loads and returns database credentials from environment variables.
    """

    db_type = db_type.lower().strip()

    if db_type not in SUPPORTED_DB_TYPES:
        raise ValueError(
            f"Unsupported database type: '{db_type}'. "
            f"Choose from: {', '.join(sorted(SUPPORTED_DB_TYPES))}"
        )

    if db_type == "sqlite":
        return _load_sqlite_credentials()

    return {"url": _require_env("DATABASE_URL")}


def validate_env(db_type: str) -> dict:
    """
    checks that all required env vars are present for the given db_type without actually returning their values. 
    useful for a health-check endpoint at startup.
    """

    db_type = db_type.lower().strip()
    required = _required_vars(db_type)
    missing = [var for var in required if not os.environ.get(var)]

    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "db_type": db_type,
    }


# credential loaders.
def _load_sqlite_credentials() -> dict:
    path = _require_env("DB_SQLITE_PATH")
    resolved = Path(path).resolve()

    if not resolved.exists():
        raise FileNotFoundError(
            f"SQLite database file not found: '{resolved}'. "
            f"Check DB_SQLITE_PATH in your .env file."
        )

    return {"database": str(resolved)}


# helpers.
def _require_env(var: str) -> str:
    """
    gets an env var or raises a clear error if it's missing.
    """

    value = os.environ.get(var)
    if not value:
        raise KeyError(
            f"Required environment variable '{var}' is not set. "
            f"Add it to your .env file."
        )
    return value


def _required_vars(db_type: str) -> list[str]:
    """
    returns the list of required env var names for each db type.
    """
    
    if db_type == "sqlite":
        return ["DB_SQLITE_PATH"]
    if db_type in ("postgresql", "mysql"):
        return ["DATABASE_URL"]
    return []