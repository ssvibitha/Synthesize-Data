"""
ZohoAnalytics local wrapper.

Drop-in replacement for the Zoho Analytics Code Studio ``ZohoAnalytics``
module so that ML scripts (AccountsHealthScore, LeadConversionZA, etc.)
can run on a local machine against CSV files without any code changes.

Usage
-----
    from ZohoAnalytics import ZohoAnalytics

The wrapper exposes the same surface that the ML scripts consume:

    za = ZohoAnalytics()
    za.context.log.INFO("hello")       # logging
"""

import logging
import os
import sys


# ---------------------------------------------------------------------------
# Logger that mirrors the Code Studio log interface (log.INFO / log.ERROR)
# ---------------------------------------------------------------------------
class _Logger:
    """Lightweight logger matching ``self.za.context.log`` from Code Studio."""

    def __init__(self, name: str = "ZohoAnalytics"):
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter("[%(levelname)s] %(message)s")
            )
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.DEBUG)

    # Code Studio uses UPPER-CASE method names
    def INFO(self, msg):  # noqa: N802
        self._logger.info(msg)

    def ERROR(self, msg):  # noqa: N802
        self._logger.error(msg)

    def WARNING(self, msg):  # noqa: N802
        self._logger.warning(msg)

    def DEBUG(self, msg):  # noqa: N802
        self._logger.debug(msg)


# ---------------------------------------------------------------------------
# Context shim (za.context.log, za.context.xxx)
# ---------------------------------------------------------------------------
class _Context:
    """Mimics ``ZohoAnalytics.context`` from Code Studio."""

    def __init__(self):
        self.log = _Logger()


# ---------------------------------------------------------------------------
# ZohoAnalytics main class
# ---------------------------------------------------------------------------
class ZohoAnalytics:
    """Local stand-in for the Zoho Analytics Code Studio runtime.

    The real Code Studio injects a ``ZohoAnalytics`` instance into every
    script with helpers for table I/O, logging, etc.  This wrapper provides
    just enough surface so that the existing ``MLModel`` classes work
    unchanged when run locally.
    """

    def __init__(self):
        self.context = _Context()
