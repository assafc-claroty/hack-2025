"""
Natural language parser using spaCy for dependency tree analysis.
"""

from typing import Any, Dict, List, Optional

import spacy
from spacy.tokens import Doc, Token

from .constants import (
    MAX_DEPENDENCY_DEPTH,
    MAX_LIMIT_SEARCH_DISTANCE,
    MAX_PROXIMITY_DISTANCE,
)
from .entity_recognizer import EntityRecognizer
from .schema import BOOLEAN_COLUMNS


class QueryParser:
    """Parses natural language queries using spaCy's linguistic features."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the query parser.

        Args:
            model_name: Name of the spaCy model to use
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError as e:
            raise RuntimeError(
                f"spaCy model '{model_name}' not found. "
                f"Please install it with: python -m spacy download {model_name}"
            ) from e

        self.entity_recognizer = EntityRecognizer(self.nlp)

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query.

        Args:
            query: Natural language query string

        Returns:
            Dictionary containing parsed components
        """
        doc = self.nlp(query)
        entities = self.entity_recognizer.recognize(doc)

        # Analyze dependency structure
        conditions = self._extract_conditions(doc, entities)

        # Determine select columns
        select_columns = self._determine_select_columns(doc, entities)

        # Extract ordering and limit
        order_by = self._extract_ordering(doc, entities)
        limit = self._extract_limit(doc, entities)

        return {
            "doc": doc,
            "entities": entities,
            "conditions": conditions,
            "select": select_columns,
            "order_by": order_by,
            "limit": limit,
        }

    def _extract_conditions(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Extract WHERE conditions from the query using dependency tree analysis.

        Args:
            doc: spaCy processed document
            entities: Recognized entities

        Returns:
            List of condition dictionaries
        """
        if not doc or not entities:
            return []

        # Extract conditions using multiple strategies
        conditions = []
        conditions.extend(self._extract_column_value_conditions(doc, entities))
        conditions.extend(self._extract_boolean_conditions(doc, entities))

        # Apply logic connectors
        if len(conditions) > 1:
            self._apply_logic_connectors(conditions, entities)

        return conditions

    def _extract_column_value_conditions(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Extract conditions for column-value pairs.

        Args:
            doc: spaCy processed document
            entities: Recognized entities

        Returns:
            List of condition dictionaries
        """
        conditions = []
        doc_len = len(doc)

        for col_entity in entities["columns"]:
            col_idx = col_entity["start"]

            # Validate index
            if col_idx < 0 or col_idx >= doc_len:
                continue

            column_name = col_entity["column"]
            col_token = doc[col_idx]

            # Try dependency-based matching first
            related_values = self._find_related_values_by_dependency(
                col_token, doc, entities
            )

            if related_values:
                conditions.extend(
                    self._create_conditions_from_values(
                        column_name, col_token, related_values, doc, entities, doc_len
                    )
                )
            else:
                # Fallback to proximity-based matching
                conditions.extend(
                    self._create_conditions_by_proximity(
                        column_name, col_idx, doc, entities
                    )
                )

        return conditions

    def _create_conditions_from_values(
        self,
        column_name: str,
        col_token: Token,
        related_values: List[Dict[str, Any]],
        doc: Doc,
        entities: Dict[str, List[Dict[str, Any]]],
        doc_len: int
    ) -> List[Dict[str, Any]]:
        """
        Create conditions from related values found via dependency analysis.

        Args:
            column_name: Name of the column
            col_token: Column token
            related_values: List of related value entities
            doc: spaCy document
            entities: Recognized entities
            doc_len: Document length

        Returns:
            List of condition dictionaries
        """
        conditions = []

        for val_entity in related_values:
            val_idx = val_entity["start"]

            # Validate value index
            if val_idx < 0 or val_idx >= doc_len:
                continue

            operator = self._infer_operator_from_dependency(
                col_token, doc[val_idx], doc, entities, column_name
            )

            condition = {
                "column": column_name,
                "operator": operator,
                "value": val_entity["value"],
            }

            if condition not in conditions:
                conditions.append(condition)

        return conditions

    def _create_conditions_by_proximity(
        self,
        column_name: str,
        col_idx: int,
        doc: Doc,
        entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Create conditions using proximity-based matching.

        Args:
            column_name: Name of the column
            col_idx: Column token index
            doc: spaCy document
            entities: Recognized entities

        Returns:
            List of condition dictionaries
        """
        conditions = []

        for val_entity in entities["values"]:
            val_idx = val_entity["start"]

            # Check if value is reasonably close to column
            if abs(val_idx - col_idx) <= MAX_PROXIMITY_DISTANCE:
                operator = self._infer_operator(
                    doc, col_idx, val_idx, entities, column_name
                )

                condition = {
                    "column": column_name,
                    "operator": operator,
                    "value": val_entity["value"],
                }

                if condition not in conditions:
                    conditions.append(condition)

        return conditions

    def _extract_boolean_conditions(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Extract conditions for boolean columns without explicit values.

        Args:
            doc: spaCy processed document
            entities: Recognized entities

        Returns:
            List of condition dictionaries
        """
        conditions = []
        doc_len = len(doc)

        for col_entity in entities["columns"]:
            column_name = col_entity["column"]
            col_idx = col_entity["start"]

            # Validate index
            if col_idx < 0 or col_idx >= doc_len:
                continue

            if column_name not in BOOLEAN_COLUMNS:
                continue

            # Check for negation
            col_token = doc[col_idx]
            is_negated = self._is_negated(col_token)

            conditions.append({
                "column": column_name,
                "operator": "=",
                "value": not is_negated,
            })

        return conditions

    def _apply_logic_connectors(
        self,
        conditions: List[Dict[str, Any]],
        entities: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """
        Apply logical connectors (AND/OR) to conditions.

        Args:
            conditions: List of conditions to modify
            entities: Recognized entities
        """
        logic_type = self._determine_logic_connector(entities)
        for condition in conditions:
            condition["logic"] = logic_type

    def _infer_operator(
        self,
        doc: Doc,
        col_idx: int,
        val_idx: int,
        entities: Dict[str, List[Dict[str, Any]]],
        column_name: str,
    ) -> str:
        """
        Infer the comparison operator between a column and value.

        Args:
            doc: spaCy document
            col_idx: Column token index
            val_idx: Value token index
            entities: Recognized entities
            column_name: Name of the column

        Returns:
            Operator string
        """
        # Check for explicit operators between column and value
        start = min(col_idx, val_idx)
        end = max(col_idx, val_idx)

        for op_entity in entities["operators"]:
            if start <= op_entity["start"] <= end:
                op_type = op_entity["operator"]
                return self._map_operator(op_type)

        # Check for "in" operator
        for token in doc[start:end]:
            if token.lower_ == "in":
                return "="

        # Check dependency relations
        col_token = doc[col_idx]
        val_token = doc[val_idx]

        # Look for negation
        if self._is_negated(col_token) or self._is_negated(val_token):
            return "!="

        # Check for "like" patterns (contains, includes)
        for token in doc[start:end]:
            if token.lower_ in ["contains", "like", "includes", "has"]:
                return "LIKE"

        # Default to equality
        return "="

    def _map_operator(self, op_type: str) -> str:
        """Map operator type to SQL operator."""
        mapping = {
            "equals": "=",
            "not_equals": "!=",
            "greater": ">",
            "less": "<",
            "like": "LIKE",
            "in": "IN",
        }
        return mapping.get(op_type, "=")

    def _is_negated(self, token: Token) -> bool:
        """Check if a token is negated."""
        # Check for negation in dependencies
        for child in token.children:
            if child.dep_ == "neg":
                return True

        # Check if token has a negation ancestor
        for ancestor in token.ancestors:
            if ancestor.lower_ in ["not", "no", "never"]:
                return True

        return False

    def _determine_logic_connector(
        self, entities: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """
        Determine the logical connector (AND/OR) for multiple conditions.

        Args:
            entities: Recognized entities

        Returns:
            Logic connector string ("AND" or "OR")
        """
        # Check for explicit OR
        for logic_entity in entities["logic"]:
            if logic_entity["type"] == "or":
                return "OR"

        # Default to AND
        return "AND"

    def _determine_select_columns(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """
        Determine which columns to select.

        Args:
            doc: spaCy document
            entities: Recognized entities

        Returns:
            List of column names to select
        """
        # For now, default to all columns
        # Could be extended to parse specific column requests
        return ["*"]

    def _extract_ordering(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, str]]:
        """
        Extract ORDER BY clauses.

        Args:
            doc: spaCy document
            entities: Recognized entities

        Returns:
            List of ordering dictionaries
        """
        order_by = []

        # Look for ordering keywords
        for token in doc:
            if token.lower_ in ["sort", "order", "sorted", "ordered"]:
                # Look for "by" and column name
                for child in token.children:
                    if child.lower_ == "by":
                        # Find column after "by"
                        for col_entity in entities["columns"]:
                            if col_entity["start"] > child.i:
                                direction = "ASC"
                                # Check for desc/descending
                                for t in doc[child.i:col_entity["end"] + 3]:
                                    if t.lower_ in ["desc", "descending", "reverse"]:
                                        direction = "DESC"

                                order_by.append({
                                    "column": col_entity["column"],
                                    "direction": direction,
                                })
                                break

        return order_by

    def _extract_limit(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> Optional[int]:
        """
        Extract LIMIT clause.

        Args:
            doc: spaCy document
            entities: Recognized entities

        Returns:
            Limit value or None
        """
        # Look for "limit", "top", "first" keywords
        for i, token in enumerate(doc):
            if token.lower_ in ["limit", "top", "first"]:
                # Look for a number nearby
                for val_entity in entities["values"]:
                    if (val_entity["type"] == "integer" and
                        abs(val_entity["start"] - i) <= MAX_LIMIT_SEARCH_DISTANCE):
                        limit_val = val_entity["value"]
                        if isinstance(limit_val, int):
                            return limit_val

        return None

    def _find_related_values_by_dependency(
        self, col_token: Token, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Find values related to a column using dependency tree analysis.

        Uses spaCy's dependency parsing to find semantic relationships between
        column mentions and their values, following paths like:
        - Direct object relationships (dobj, pobj)
        - Prepositional attachments (prep, pcomp)
        - Attribute relationships (attr, amod)

        Args:
            col_token: The token representing the column
            doc: spaCy document
            entities: Recognized entities

        Returns:
            List of related value entities
        """
        related_values = []
        value_positions = {v["start"]: v for v in entities["values"]}

        # Strategy 1: Check direct children and descendants
        for child in col_token.children:
            if child.i in value_positions:
                related_values.append(value_positions[child.i])

            # Check grandchildren for prepositional phrases
            for grandchild in child.children:
                if grandchild.i in value_positions:
                    related_values.append(value_positions[grandchild.i])

        # Strategy 2: Check ancestors (column might be dependent on value)
        for ancestor in col_token.ancestors:
            # Look for values in ancestor's children
            for sibling in ancestor.children:
                if sibling.i in value_positions and sibling.i != col_token.i:
                    related_values.append(value_positions[sibling.i])

        # Strategy 3: Check siblings (parallel structure)
        if col_token.head:
            for sibling in col_token.head.children:
                if sibling.i in value_positions and sibling.i != col_token.i:
                    # Check if they're in a reasonable relationship
                    if sibling.dep_ in ["dobj", "pobj", "attr", "nummod"]:
                        related_values.append(value_positions[sibling.i])

        # Strategy 4: Find values connected via prepositions
        for token in doc:
            if token.dep_ == "prep" and token.head == col_token:
                # Look for values after the preposition
                for child in token.children:
                    if child.i in value_positions:
                        related_values.append(value_positions[child.i])

        return related_values

    def _infer_operator_from_dependency(
        self,
        col_token: Token,
        val_token: Token,
        doc: Doc,
        entities: Dict[str, List[Dict[str, Any]]],
        column_name: str,
    ) -> str:
        """
        Infer operator using dependency relationships.

        Analyzes the dependency path between column and value tokens to
        determine the appropriate SQL operator.

        Args:
            col_token: Column token
            val_token: Value token
            doc: spaCy document
            entities: Recognized entities
            column_name: Name of the column

        Returns:
            SQL operator string
        """
        # Check for explicit operators in the dependency path
        path_tokens = self._get_dependency_path(col_token, val_token)

        for token in path_tokens:
            # Check for negation
            if token.lower_ in ["not", "no", "never"] or token.dep_ == "neg":
                return "!="

            # Check for comparison keywords
            if token.lower_ in ["greater", "more", "above", "over"]:
                return ">"
            if token.lower_ in ["less", "fewer", "below", "under"]:
                return "<"
            if token.lower_ in ["contains", "like", "includes", "has", "with"]:
                return "LIKE"
            if token.lower_ in ["starts", "begins"]:
                return "LIKE"  # Will be formatted as 'value%'
            if token.lower_ in ["ends", "finishes"]:
                return "LIKE"  # Will be formatted as '%value'

        # Check dependency labels
        if val_token.dep_ in ["pobj", "dobj"]:
            # Check if there's a preposition
            if val_token.head.pos_ == "ADP":
                prep = val_token.head.lower_
                if prep == "in":
                    return "="
                elif prep in ["with", "containing"]:
                    return "LIKE"

        # Check for "affected by", "vulnerable to" patterns
        if col_token.head.lower_ in ["affected", "vulnerable", "impacted"]:
            return "LIKE"  # For CVE and vulnerability queries

        # Default to equality
        return "="

    def _get_dependency_path(self, token1: Token, token2: Token) -> List[Token]:
        """
        Get the dependency path between two tokens.

        Args:
            token1: First token
            token2: Second token

        Returns:
            List of tokens in the path
        """
        # Find common ancestor
        ancestors1 = set([token1] + list(token1.ancestors))
        ancestors2 = set([token2] + list(token2.ancestors))

        common = ancestors1 & ancestors2
        if not common:
            return []

        # Get path through lowest common ancestor
        try:
            lca = min(common, key=lambda t: t.i)
        except (ValueError, AttributeError):
            return []

        # Build path from token1 to lca with safety limit
        path = []
        current = token1
        depth = 0

        while current != lca and current is not None and depth < MAX_DEPENDENCY_DEPTH:
            path.append(current)
            # Check for ROOT token (where head == self)
            if current.head == current:
                break
            current = current.head
            depth += 1

        if depth >= MAX_DEPENDENCY_DEPTH:
            # Return partial path if we hit the limit
            return path

        path.append(lca)

        # Build path from lca to token2 with safety limit
        path2 = []
        current = token2
        depth = 0

        while current != lca and current is not None and depth < MAX_DEPENDENCY_DEPTH:
            path2.append(current)
            # Check for ROOT token (where head == self)
            if current.head == current:
                break
            current = current.head
            depth += 1

        path.extend(reversed(path2))

        return path

    def get_dependency_tree_info(self, query: str) -> Dict[str, Any]:
        """
        Get detailed dependency tree information for debugging.

        Args:
            query: Natural language query

        Returns:
            Dictionary with dependency tree information
        """
        doc = self.nlp(query)

        tree_info: Dict[str, Any] = {
            "tokens": [],
            "dependencies": [],
            "noun_chunks": [],
            "entities": [],
        }

        for token in doc:
            tree_info["tokens"].append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "head": token.head.text,
                "children": [child.text for child in token.children],
            })

            tree_info["dependencies"].append({
                "token": token.text,
                "dep": token.dep_,
                "head": token.head.text,
            })

        for chunk in doc.noun_chunks:
            tree_info["noun_chunks"].append({
                "text": chunk.text,
                "root": chunk.root.text,
                "dep": chunk.root.dep_,
            })

        for ent in doc.ents:
            tree_info["entities"].append({
                "text": ent.text,
                "label": ent.label_,
            })

        return tree_info

