"""Structured logging utility for FINORA AI Multi-Agent System."""

import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(name)-24s | %(levelname)-7s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "finora_ai") -> logging.Logger:
    """Return a configured logger instance with standard FINORA AI formatting.

    Args:
        name: Name of the logger, typically the module or agent name.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger

