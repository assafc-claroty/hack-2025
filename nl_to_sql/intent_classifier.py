"""
Intent classification for natural language queries.
"""

from typing import Any, Dict, List, Optional

from spacy.tokens import Doc

from .schema import MULTI_VALUE_COLUMNS, TEXT_LIST_COLUMNS


class IntentClassifier:
    """Classifies the intent of natural language queries."""

    # Intent types
    INTENT_SELECT = "select"
    INTENT_COUNT = "count"
    INTENT_EXISTS = "exists"

    def __init__(self) -> None:
        """Initialize the intent classifier."""
        self.intent_keywords = {
            self.INTENT_SELECT: [
                "show", "display", "list", "get", "find", "fetch",
                "give", "return", "retrieve", "select", "view"
            ],
            self.INTENT_COUNT: [
                "count", "how many", "number of", "total"
            ],
            self.INTENT_EXISTS: [
                "has", "have", "does", "do", "is", "are",
                "exists", "exist", "any", "there"
            ],
        }

    def classify(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Classify the intent of a query.

        Args:
            doc: spaCy processed document
            entities: Recognized entities from the query

        Returns:
            Dictionary with intent information
        """
        # Early check for multi-value field queries - these should always be SELECT
        # even if they start with "Has" or "Is", because we want to return ALL matching rows
        # Multi-value fields include: CVE, old_ip, active_queries, active_tasks, etc.
        if self._is_multi_value_field_query(doc, entities):
            return self._create_intent_result(self.INTENT_SELECT, doc, entities)

        # Check for explicit intent entities
        if entities.get("intent"):
            intent_type = entities["intent"][0]["type"]
            # Map entity intent types to normalized intent types
            intent_mapping = {
                "show": self.INTENT_SELECT,
                "count": self.INTENT_COUNT,
                "exists": self.INTENT_EXISTS,
            }
            normalized_intent = intent_mapping.get(intent_type, self.INTENT_SELECT)
            return self._create_intent_result(normalized_intent, doc, entities)

        # Analyze query structure using dependency parsing
        intent = self._analyze_dependency_structure(doc)

        if intent:
            return self._create_intent_result(intent, doc, entities)

        # Fallback to keyword matching
        intent = self._keyword_based_classification(doc)

        return self._create_intent_result(intent, doc, entities)

    def _analyze_dependency_structure(self, doc: Doc) -> Optional[str]:
        """
        Analyze dependency tree to determine intent.

        Args:
            doc: spaCy processed document

        Returns:
            Intent type or None
        """
        # Find the root verb
        root_verb = None
        for token in doc:
            if token.dep_ == "ROOT":
                root_verb = token
                break

        if not root_verb:
            return None

        root_lemma = root_verb.lemma_.lower()

        # Check for count intent
        if root_lemma in ["count", "be"] and any(
            t.lower_ in ["many", "much", "number"] for t in doc
        ):
            return self.INTENT_COUNT

        # Check for existence intent
        # Note: Multi-value field queries are already handled before this method is called
        if root_lemma in ["have", "be", "exist", "do"]:
            # Look for question structure
            if doc[0].lower_ in ["has", "have", "is", "are", "does", "do"]:
                return self.INTENT_EXISTS

        # Check for select intent
        if root_lemma in ["show", "display", "list", "get", "find", "give", "return"]:
            return self.INTENT_SELECT

        return None

    def _is_multi_value_field_query(self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]) -> bool:
        """
        Check if query is asking about multi-value fields.

        Multi-value field queries should return all matching rows, not just check existence.
        Examples:
        - "Has CVE-2017-12819 been remediated?" -> SELECT (not EXISTS)
        - "Show assets with old IP 192.168.1.1" -> SELECT
        - "Find assets with active query backup_job" -> SELECT

        Args:
            doc: spaCy processed document
            entities: Recognized entities from the query

        Returns:
            True if this is a multi-value field query
        """
        text_lower = doc.text.lower()

        # Check if any multi-value column is mentioned in entities
        if entities.get("columns"):
            for col_entity in entities["columns"]:
                col_name = col_entity.get("column", "")
                if col_name in MULTI_VALUE_COLUMNS or col_name in TEXT_LIST_COLUMNS:
                    return True

        # Check for multi-value field keywords in the query text
        multi_value_keywords = {
            # CVE/vulnerability related
            "cve", "vulnerability", "vulnerabilities", "remediat", "patch", "fix",
            # IP related
            "old_ip", "old ip", "previous ip",
            # Query/task related
            "active_queries", "active queries", "active_tasks", "active tasks",
            "running query", "running queries", "running task", "running tasks",
            # Other multi-value fields
            "children", "code_sections", "asset_insight", "insight_names",
            "custom_information", "custom_attributes",
        }

        # Check if any multi-value keyword is in the query
        for keyword in multi_value_keywords:
            if keyword in text_lower:
                return True

        return False

    def _keyword_based_classification(self, doc: Doc) -> str:
        """
        Classify intent based on keyword matching.

        Args:
            doc: spaCy processed document

        Returns:
            Intent type (defaults to SELECT)
        """
        text_lower = doc.text.lower()

        # Check for count keywords
        for keyword in self.intent_keywords[self.INTENT_COUNT]:
            if keyword in text_lower:
                return self.INTENT_COUNT

        # Check for existence keywords (but be careful with false positives)
        if text_lower.startswith(("has ", "have ", "is ", "are ", "does ", "do ")):
            return self.INTENT_EXISTS

        # Check for select keywords
        for keyword in self.intent_keywords[self.INTENT_SELECT]:
            if keyword in text_lower:
                return self.INTENT_SELECT

        # Default to SELECT
        return self.INTENT_SELECT

    def _create_intent_result(
        self, intent_type: str, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Create a structured intent result.

        Args:
            intent_type: Type of intent
            doc: spaCy document
            entities: Recognized entities

        Returns:
            Intent result dictionary
        """
        result = {
            "type": intent_type,
            "confidence": 1.0,  # Could be enhanced with confidence scoring
        }

        # Add intent-specific information
        if intent_type == self.INTENT_COUNT:
            result["aggregation"] = "COUNT"
            result["select_columns"] = ["COUNT(*)"]

        elif intent_type == self.INTENT_EXISTS:
            result["aggregation"] = "EXISTS"
            # Could add LIMIT 1 for optimization
            result["limit"] = 1

        elif intent_type == self.INTENT_SELECT:
            result["aggregation"] = None
            # Determine if all columns or specific ones
            result["select_columns"] = ["*"]

        return result

    def requires_aggregation(self, intent: Dict[str, Any]) -> bool:
        """
        Check if the intent requires aggregation.

        Args:
            intent: Intent result dictionary

        Returns:
            True if aggregation is needed
        """
        return intent.get("aggregation") is not None

    def get_select_columns(self, intent: Dict[str, Any]) -> List[str]:
        """
        Get the columns to select based on intent.

        Args:
            intent: Intent result dictionary

        Returns:
            List of column names or expressions
        """
        columns = intent.get("select_columns", ["*"])
        if not isinstance(columns, list):
            return ["*"]
        return columns

