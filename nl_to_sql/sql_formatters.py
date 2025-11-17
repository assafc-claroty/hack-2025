"""
SQL value formatters to handle different data types.

This module fixes the feature envy issue in QueryBuilder.to_sql()
by extracting value formatting logic into dedicated classes.
"""

from abc import ABC, abstractmethod
from typing import Any

from .schema import MULTI_VALUE_COLUMNS


class SQLValueFormatter(ABC):
    """Base class for SQL value formatters."""

    @abstractmethod
    def format(self, value: Any, column: str, operator: str) -> str:
        """
        Format value for SQL.

        Args:
            value: Value to format
            column: Column name
            operator: SQL operator

        Returns:
            Formatted SQL value string
        """
        pass


class BooleanValueFormatter(SQLValueFormatter):
    """Formats boolean values for SQL."""

    def format(self, value: Any, column: str, operator: str) -> str:
        """Format boolean value."""
        return str(value).upper()


class NumericValueFormatter(SQLValueFormatter):
    """Formats numeric values (int, float) for SQL."""

    def format(self, value: Any, column: str, operator: str) -> str:
        """Format numeric value."""
        return str(value)


class StringValueFormatter(SQLValueFormatter):
    """Formats string values for SQL."""

    def format(self, value: Any, column: str, operator: str) -> str:
        """Format string value."""
        escaped = self._escape_sql_string(value)

        # Adjust operator for multi-value columns
        if column in MULTI_VALUE_COLUMNS and operator == "=":
            operator = "LIKE"

        if operator == "LIKE":
            escaped = self._escape_like_wildcards(escaped)
            # Check if this is an IP prefix (partial IP address)
            if column == "ipv4" and self._is_ip_prefix(value):
                # For IP prefixes like "10.89", use prefix matching
                return f"'{escaped}%'"
            return f"'%{escaped}%'"

        return f"'{escaped}'"

    def _escape_sql_string(self, value: str) -> str:
        """Escape single quotes for SQL."""
        return value.replace("'", "''")

    def _escape_like_wildcards(self, value: str) -> str:
        """Escape LIKE wildcards."""
        return value.replace("%", "\\%").replace("_", "\\_")
    
    def _is_ip_prefix(self, value: str) -> bool:
        """Check if value is an IP prefix (partial IP)."""
        if not isinstance(value, str):
            return False
        parts = value.split('.')
        # IP prefix has 2-3 parts (not full 4)
        return 2 <= len(parts) < 4 and all(part.isdigit() for part in parts)


class DefaultValueFormatter(SQLValueFormatter):
    """Default formatter for unknown types."""

    def format(self, value: Any, column: str, operator: str) -> str:
        """Format value using str()."""
        return str(value)


class SQLValueFormatterFactory:
    """Factory for creating SQL value formatters."""

    def __init__(self):
        """Initialize formatter factory."""
        self.formatters = {
            bool: BooleanValueFormatter(),
            str: StringValueFormatter(),
            int: NumericValueFormatter(),
            float: NumericValueFormatter(),
        }
        self.default_formatter = DefaultValueFormatter()

    def get_formatter(self, value: Any) -> SQLValueFormatter:
        """
        Get appropriate formatter for value type.

        Args:
            value: Value to format

        Returns:
            Appropriate formatter instance
        """
        return self.formatters.get(type(value), self.default_formatter)

    def format(self, value: Any, column: str, operator: str) -> str:
        """
        Format value for SQL.

        Args:
            value: Value to format
            column: Column name
            operator: SQL operator

        Returns:
            Formatted SQL value string
        """
        formatter = self.get_formatter(value)
        return formatter.format(value, column, operator)

