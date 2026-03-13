"""
centralised logging configuration for the entire project.
import this logger in any module that needs to be logged.

usage:
    
    from core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("connected to database")
    logger.error("something failed", exc_info=True)
    
"""


import logging
import os
from logging.handlers import RotatingFileHandler


# log level is controlled via the LOG_LEVEL env var (default: INFO)
LOG_LEVEL   = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT  = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_root_logger() -> logging.Logger:
    root = logging.getLogger("text_to_sql")
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # avoid adding duplicate handlers if this is called more than once
    if root.handlers:
        return root

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # console handler — always on, prints to stdout
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    # rotating file handler - writes to logs/app.log
    # rotates at 5MB and keeps the last 3 log files so logs never eat disk space
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename    = os.path.join(log_dir, "app.log"),
        maxBytes    = 5 * 1024 * 1024,  # 5MB
        backupCount = 3,
        encoding    = "utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    return root


# initialise once at import time
_root_logger = _build_root_logger()


def get_logger(name: str) -> logging.Logger:

    return _root_logger.getChild(name)