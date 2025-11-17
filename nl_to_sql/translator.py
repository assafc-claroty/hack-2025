"""
Main translator interface for converting natural language to SQL queries.
"""

import json
from typing import Any, Dict, Literal

from .intent_classifier import IntentClassifier
from .parser import QueryParser
from .query_builder import QueryBuilder

OutputFormat = Literal["sql", "json", "both"]


class NLToSQLTranslator:
    """
    Main interface for translating natural language queries to SQL.

    This class orchestrates the entire pipeline:
    1. Parse the natural language query using spaCy
    2. Classify the intent of the query
    3. Build a JSON representation of the SQL query
    """

    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        table_name: str = "assets",
        output_format: OutputFormat = "sql",
    ):
        """
        Initialize the translator.

        Args:
            model_name: Name of the spaCy model to use
            table_name: Name of the database table
            output_format: Default output format ("sql", "json", or "both")
        """
        self.parser = QueryParser(model_name=model_name)
        self.intent_classifier = IntentClassifier()
        self.query_builder = QueryBuilder(table_name=table_name)
        self.output_format = output_format

    def translate(self, query: str) -> Dict[str, Any]:
        """
        Translate a natural language query to a JSON SQL representation.

        Args:
            query: Natural language query string

        Returns:
            Dictionary containing the JSON representation of the SQL query

        Example:
            >>> translator = NLToSQLTranslator()
            >>> result = translator.translate("Show me all assets in site 54")
            >>> print(result)
            {
                "table": "assets",
                "select": ["*"],
                "where": [{"column": "site", "operator": "=", "value": 54}],
                "order_by": [],
                "limit": None
            }
        """
        # Step 1: Parse the query
        parsed_data = self.parser.parse(query)

        # Step 2: Classify the intent
        intent = self.intent_classifier.classify(
            parsed_data["doc"], parsed_data["entities"]
        )

        # Step 3: Build the JSON query
        query_json = self.query_builder.build(parsed_data, intent)

        return query_json

    def translate_to_sql(self, query: str) -> str:
        """
        Translate a natural language query directly to a SQL string.

        Args:
            query: Natural language query string

        Returns:
            SQL query string

        Example:
            >>> translator = NLToSQLTranslator()
            >>> sql = translator.translate_to_sql("Show me all assets in site 54")
            >>> print(sql)
            SELECT * FROM assets WHERE site = 54
        """
        query_json = self.translate(query)
        return self.query_builder.to_sql(query_json)
    
    def translate_with_format(
        self, 
        query: str, 
        output_format: OutputFormat = None
    ) -> str | Dict[str, Any]:
        """
        Translate a query and return in the specified format.

        Args:
            query: Natural language query string
            output_format: Output format ("sql", "json", or "both"). 
                          If None, uses the instance's default format.

        Returns:
            - If format is "sql": SQL query string
            - If format is "json": Dictionary with JSON representation
            - If format is "both": Dictionary with both "sql" and "json" keys

        Examples:
            >>> translator = NLToSQLTranslator(output_format="sql")
            >>> result = translator.translate_with_format("Show me all assets")
            >>> print(result)
            SELECT * FROM assets

            >>> translator = NLToSQLTranslator(output_format="json")
            >>> result = translator.translate_with_format("Show me all assets")
            >>> print(result)
            {'table': 'assets', 'select': ['*'], 'where': [], ...}

            >>> translator = NLToSQLTranslator(output_format="both")
            >>> result = translator.translate_with_format("Show me all assets")
            >>> print(result["sql"])
            SELECT * FROM assets
            >>> print(result["json"])
            {'table': 'assets', 'select': ['*'], 'where': [], ...}
        """
        # Use instance default if not specified
        if output_format is None:
            output_format = self.output_format
        
        # Get JSON representation
        query_json = self.translate(query)
        
        # Return based on format
        if output_format == "sql":
            return self.query_builder.to_sql(query_json)
        elif output_format == "json":
            return query_json
        elif output_format == "both":
            return {
                "sql": self.query_builder.to_sql(query_json),
                "json": query_json
            }
        else:
            raise ValueError(f"Invalid output_format: {output_format}. Must be 'sql', 'json', or 'both'")
    
    def format_output(
        self, 
        query_json: Dict[str, Any], 
        output_format: OutputFormat = None,
        pretty: bool = False
    ) -> str:
        """
        Format a query JSON into the specified output format as a string.

        Args:
            query_json: JSON representation of the query
            output_format: Output format ("sql", "json", or "both")
            pretty: If True, pretty-print JSON output

        Returns:
            Formatted string representation

        Example:
            >>> translator = NLToSQLTranslator()
            >>> query_json = translator.translate("Show me all assets")
            >>> print(translator.format_output(query_json, "sql"))
            SELECT * FROM assets
            >>> print(translator.format_output(query_json, "json", pretty=True))
            {
              "table": "assets",
              "select": ["*"],
              ...
            }
        """
        if output_format is None:
            output_format = self.output_format
        
        if output_format == "sql":
            return self.query_builder.to_sql(query_json)
        elif output_format == "json":
            if pretty:
                return json.dumps(query_json, indent=2)
            return json.dumps(query_json)
        elif output_format == "both":
            sql = self.query_builder.to_sql(query_json)
            json_str = json.dumps(query_json, indent=2) if pretty else json.dumps(query_json)
            return f"SQL:\n{sql}\n\nJSON:\n{json_str}"
        else:
            raise ValueError(f"Invalid output_format: {output_format}. Must be 'sql', 'json', or 'both'")

    def translate_with_details(self, query: str) -> Dict[str, Any]:
        """
        Translate a query and return detailed information about the translation.

        Args:
            query: Natural language query string

        Returns:
            Dictionary containing query JSON, intent, and parsed entities

        Example:
            >>> translator = NLToSQLTranslator()
            >>> result = translator.translate_with_details("Show me all assets in site 54")
            >>> print(result["intent"]["type"])
            select
        """
        # Parse the query
        parsed_data = self.parser.parse(query)

        # Classify the intent
        intent = self.intent_classifier.classify(
            parsed_data["doc"], parsed_data["entities"]
        )

        # Build the JSON query
        query_json = self.query_builder.build(parsed_data, intent)

        return {
            "query": query_json,
            "sql": self.query_builder.to_sql(query_json),
            "intent": intent,
            "entities": parsed_data["entities"],
        }

    def analyze_dependency_tree(self, query: str) -> Dict[str, Any]:
        """
        Analyze and return the dependency tree structure of a query.

        This method provides detailed linguistic analysis including:
        - Token-level information (POS tags, dependencies)
        - Dependency relationships
        - Noun chunks
        - Named entities

        Useful for debugging and understanding how the parser interprets queries.

        Args:
            query: Natural language query string

        Returns:
            Dictionary with dependency tree information

        Example:
            >>> translator = NLToSQLTranslator()
            >>> tree = translator.analyze_dependency_tree("Show me assets in site 54")
            >>> for token in tree["tokens"]:
            ...     print(f"{token['text']}: {token['pos']} ({token['dep']})")
        """
        return self.parser.get_dependency_tree_info(query)

    def explain_translation(self, query: str) -> str:
        """
        Provide a human-readable explanation of how a query was translated.

        Args:
            query: Natural language query string

        Returns:
            Formatted explanation string

        Example:
            >>> translator = NLToSQLTranslator()
            >>> print(translator.explain_translation("Show me assets in site 54"))
        """
        details = self.translate_with_details(query)
        tree = self.analyze_dependency_tree(query)

        explanation = []
        explanation.append(f"Query: {query}")
        explanation.append(f"\nIntent: {details['intent']['type']}")
        explanation.append(f"\nSQL: {details['sql']}")

        explanation.append("\n\nDependency Analysis:")
        explanation.append("-" * 60)
        for token in tree["tokens"]:
            explanation.append(
                f"  {token['text']:15} | POS: {token['pos']:5} | "
                f"DEP: {token['dep']:10} | HEAD: {token['head']}"
            )

        explanation.append("\n\nRecognized Entities:")
        explanation.append("-" * 60)
        for col in details["entities"]["columns"]:
            explanation.append(f"  Column: {col['column']} ('{col['text']}')")
        for val in details["entities"]["values"]:
            explanation.append(
                f"  Value: {val['value']} (type: {val['type']}, text: '{val['text']}')"
            )

        explanation.append("\n\nExtracted Conditions:")
        explanation.append("-" * 60)
        for cond in details["query"]["where"]:
            explanation.append(
                f"  {cond['column']} {cond['operator']} {cond['value']}"
            )

        return "\n".join(explanation)

