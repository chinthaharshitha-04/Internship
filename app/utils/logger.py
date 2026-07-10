"""Centralized logging configuration.

A single ``configure_logging`` call (made once at application startup)
ensures every module that does ``logging.getLogger("retail_discount_engine")``
or a child logger shares the same formatting and output stream,
instead of each module configuring its own handlers ad-hoc.
"""

from __future__ import annotations

import logging
import sys

LOGGER_NAME = "retail_discount_engine"


def configure_logging(debug: bool = False) -> logging.Logger:
    """Configure and return the application's root logger.

    Args:
        debug: If True, sets the log level to DEBUG; otherwise INFO.

    Returns:
        logging.Logger: The configured application logger.
    """

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Avoid attaching duplicate handlers if this is called more than
    # once (e.g. during test setup that re-imports the app).
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger nested under the application's root logger.

    Args:
        name: Optional suffix (e.g. ``"pricing_engine"``), producing a
            logger named ``"retail_discount_engine.pricing_engine"``.

    Returns:
        logging.Logger: The requested (child) logger.
    """

    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")
    return logging.getLogger(LOGGER_NAME)
