import logging
import os

def setup_logger(name=None, level=logging.INFO):
    """
    Sets up a Lambda-compatible logger that only writes to console.
    Lambda has a read-only filesystem except for /tmp, so we avoid file operations.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger