"""Logging configuration for the src."""

import logging
import sys

logger = logging.getLogger("CS2 Battle Bot")

stdout = logging.StreamHandler(stream=sys.stdout)

fmt = logging.Formatter(
    "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s"
)

stdout.setFormatter(fmt)
logger.addHandler(stdout)

logger.setLevel(logging.DEBUG)
