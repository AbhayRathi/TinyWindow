"""Structured logging utilities for TinyWindow."""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Raises:
        ValueError: If an invalid logging level is provided
    """
    try:
        log_level = getattr(logging, level)
    except AttributeError as e:
        raise ValueError(f"Invalid logging level: {level}") from e

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
