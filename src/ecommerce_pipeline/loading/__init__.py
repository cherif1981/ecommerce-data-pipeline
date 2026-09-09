"""Loading module for the ETL pipeline."""

from .postgres import DatabaseLoader

__all__ = ["DatabaseLoader"]