"""
Query builder for constructing JSON representations of SQL queries.
"""

from typing import Any, Dict, List, Optional

from .schema import MULTI_VALUE_COLUMNS


class QueryBuilder:
    """Builds JSON representations of SQL queries from parsed components."""

    def __init__(self, table_name: str = "assets"):
        """
        Initialize the query builder.

        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name

    def build(
        self,
        parsed_data: Dict[str, Any],
        intent: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build a JSON representation of a SQL query.

        Args:
            parsed_data: Parsed query components from QueryParser
            intent: Intent classification result

        Returns:
            JSON representation of the SQL query
        """
        query = {
            "table": self.table_name,
            "select": self._build_select(parsed_data, intent),
            "where": self._build_where(parsed_data),
            "order_by": self._build_order_by(parsed_data),
            "limit": self._build_limit(parsed_data, intent),
        }

        return query

    def _build_select(
        self, parsed_data: Dict[str, Any], intent: Dict[str, Any]
    ) -> List[str]:
        """
        Build the SELECT clause.

        Args:
            parsed_data: Parsed query components
            intent: Intent classification

        Returns:
            List of columns/expressions to select
        """
        # Check if intent specifies special select columns (e.g., COUNT)
        if "select_columns" in intent:
            columns = intent["select_columns"]
            if isinstance(columns, list):
                return columns
            return ["*"]

        # Use columns from parsed data
        select_columns = parsed_data.get("select", ["*"])
        if isinstance(select_columns, list):
            return select_columns

        return ["*"]

    def _build_where(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build the WHERE clause.

        Args:
            parsed_data: Parsed query components

        Returns:
            List of condition dictionaries
        """
        conditions = parsed_data.get("conditions", [])

        # Format conditions for JSON output
        formatted_conditions = []

        for condition in conditions:
            formatted_condition = {
                "column": condition["column"],
                "operator": condition["operator"],
                "value": condition["value"],
            }

            # Add logic connector if present
            if "logic" in condition:
                formatted_condition["logic"] = condition["logic"]

            formatted_conditions.append(formatted_condition)

        return formatted_conditions

    def _build_order_by(self, parsed_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Build the ORDER BY clause.

        Args:
            parsed_data: Parsed query components

        Returns:
            List of ordering dictionaries
        """
        order_by = parsed_data.get("order_by", [])
        if isinstance(order_by, list):
            return order_by
        return []

    def _build_limit(
        self, parsed_data: Dict[str, Any], intent: Dict[str, Any]
    ) -> Optional[int]:
        """
        Build the LIMIT clause.

        Args:
            parsed_data: Parsed query components
            intent: Intent classification

        Returns:
            Limit value or None
        """
        # Check if intent specifies a limit (e.g., for EXISTS queries)
        if "limit" in intent and intent["limit"] is not None:
            limit_val = intent["limit"]
            if isinstance(limit_val, int):
                return limit_val
            return None

        # Use limit from parsed data
        limit_val = parsed_data.get("limit")
        if isinstance(limit_val, int):
            return limit_val
        return None

    def to_sql(self, query_json: Dict[str, Any]) -> str:
        """
        Convert JSON query representation to SQL string (helper method).

        Args:
            query_json: JSON representation of query

        Returns:
            SQL query string
        """
        # Build SELECT clause
        select_cols = ", ".join(query_json["select"])
        sql = f"SELECT {select_cols} FROM {query_json['table']}"

        # Build WHERE clause
        if query_json["where"]:
            where_parts = []

            for i, condition in enumerate(query_json["where"]):
                col = condition["column"]
                op = condition["operator"]
                val = condition["value"]

                # Format value based on type
                if isinstance(val, bool):
                    val_str = str(val).upper()
                elif isinstance(val, str):
                    # Escape single quotes to prevent SQL injection
                    escaped_val = val.replace("'", "''")

                    # Multi-value columns should always use LIKE for pattern matching
                    # since they contain multiple values (comma-separated, JSON arrays, etc.)
                    if col in MULTI_VALUE_COLUMNS and op == "=":
                        op = "LIKE"

                    # Handle LIKE operator
                    if op == "LIKE":
                        # Escape LIKE wildcards in user input
                        escaped_val = escaped_val.replace("%", "\\%").replace("_", "\\_")
                        val_str = f"'%{escaped_val}%'"
                    else:
                        val_str = f"'{escaped_val}'"
                else:
                    val_str = str(val)

                where_parts.append(f"{col} {op} {val_str}")

                # Add logic connector for next condition
                if i < len(query_json["where"]) - 1:
                    logic = condition.get("logic", "AND")
                    where_parts.append(logic)

            sql += " WHERE " + " ".join(where_parts)

        # Build ORDER BY clause
        if query_json["order_by"]:
            order_parts = [
                f"{o['column']} {o['direction']}"
                for o in query_json["order_by"]
            ]
            sql += " ORDER BY " + ", ".join(order_parts)

        # Build LIMIT clause
        if query_json["limit"] is not None:
            sql += f" LIMIT {query_json['limit']}"

        return sql

