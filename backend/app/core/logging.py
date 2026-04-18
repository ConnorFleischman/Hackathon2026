"""Application-wide logging setup."""

import logging
import sys


def configure_logging() -> None:
    """Basic structured-friendly logging; extend with JSON/formatters as needed."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
    )
