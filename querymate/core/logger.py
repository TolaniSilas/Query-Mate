import os
import logging
from logging.handlers import RotatingFileHandler


LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_root_logger() -> logging.Logger:
    root = logging.getLogger("query-mate")
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    if root.handlers:
        return root

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename = os.path.join(log_dir, "app.log"),
        maxBytes = 5 * 1024 * 1024, 
        backupCount = 3,
        encoding = "utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    return root


_root_logger = _build_root_logger()


def get_logger(name: str) -> logging.Logger:

    return _root_logger.getChild(name)