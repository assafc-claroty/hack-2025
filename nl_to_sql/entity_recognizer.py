"""
Entity recognition for natural language queries using spaCy patterns.
"""

from typing import Any, Dict, List

from spacy.matcher import Matcher
from spacy.tokens import Doc

from .schema import (
    COLUMN_SYNONYMS,
    MULTI_VALUE_COLUMNS,
    TEXT_LIST_COLUMNS,
    VALID_COLUMNS,
)
from .value_extractors import ValueExtractor


class EntityRecognizer:
    """Recognizes entities in natural language queries for SQL translation."""

    def __init__(self, nlp: Any) -> None:
        """
        Initialize the entity recognizer.

        Args:
            nlp: spaCy language model
        """
        self.nlp = nlp
        self.matcher = Matcher(nlp.vocab)
        self.value_extractor = ValueExtractor()
        self._setup_patterns()

    def _setup_patterns(self) -> None:
        """Setup matching patterns for entities."""

        # Column name patterns
        for column, synonyms in COLUMN_SYNONYMS.items():
            patterns = [[{"LOWER": syn}] for syn in synonyms]
            self.matcher.add(f"COLUMN_{column.upper()}", patterns)

        # Comparison operator patterns
        self.matcher.add("OP_EQUALS", [
            [{"LOWER": {"IN": ["is", "equals", "equal"]}}],
            [{"LOWER": "="}, {"LOWER": "="}],
        ])

        self.matcher.add("OP_NOT_EQUALS", [
            [{"LOWER": "not"}, {"LOWER": {"IN": ["is", "equals", "equal"]}}],
            [{"LOWER": "is"}, {"LOWER": "not"}],
            [{"LOWER": "!="}, {"LOWER": "="}],
        ])

        self.matcher.add("OP_GREATER", [
            [{"LOWER": {"IN": ["greater", "more", "above"]}}],
            [{"LOWER": ">"}, {"LOWER": ">"}],
        ])

        self.matcher.add("OP_LESS", [
            [{"LOWER": {"IN": ["less", "fewer", "below"]}}],
            [{"LOWER": "<"}, {"LOWER": "<"}],
        ])

        self.matcher.add("OP_LIKE", [
            [{"LOWER": {"IN": ["contains", "like", "includes", "has"]}}],
            [{"LOWER": "similar"}, {"LOWER": "to"}],
        ])

        self.matcher.add("OP_IN", [
            [{"LOWER": "in"}],
        ])

        # Boolean value patterns
        self.matcher.add("BOOL_TRUE", [
            [{"LOWER": {"IN": ["true", "yes", "approved", "valid", "enabled"]}}],
        ])

        self.matcher.add("BOOL_FALSE", [
            [{"LOWER": {"IN": ["false", "no", "not", "disabled", "invalid"]}}],
        ])

        # Logical connectors
        self.matcher.add("LOGIC_AND", [
            [{"LOWER": {"IN": ["and", "with"]}}],
        ])

        self.matcher.add("LOGIC_OR", [
            [{"LOWER": {"IN": ["or"]}}],
        ])

        # Query intent patterns
        self.matcher.add("INTENT_SHOW", [
            [{"LOWER": {"IN": ["show", "display", "list", "get", "find", "fetch"]}}],
        ])

        self.matcher.add("INTENT_COUNT", [
            [{"LOWER": "how"}, {"LOWER": "many"}],
            [{"LOWER": "count"}],
            [{"LOWER": "number"}, {"LOWER": "of"}],
        ])

        self.matcher.add("INTENT_EXISTS", [
            [{"LOWER": {"IN": ["has", "does", "is", "are", "exists"]}}],
        ])

        # All/any patterns
        self.matcher.add("QUANTIFIER_ALL", [
            [{"LOWER": "all"}],
            [{"LOWER": "every"}],
        ])

        self.matcher.add("QUANTIFIER_ANY", [
            [{"LOWER": "any"}],
            [{"LOWER": "some"}],
        ])

    def recognize(self, doc: Doc) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recognize entities in a spaCy Doc.

        Args:
            doc: spaCy processed document

        Returns:
            Dictionary of recognized entities by category
        """
        # Pre-process to find multi-token CVE identifiers
        # CVE identifiers are often tokenized as multiple tokens (CVE-YYYY-NNNNN)
        cve_spans = self.value_extractor.find_cve_spans(doc)

        matches = self.matcher(doc)

        entities: Dict[str, List[Dict[str, Any]]] = {
            "columns": [],
            "operators": [],
            "values": [],
            "logic": [],
            "intent": [],
            "quantifiers": [],
        }

        for match_id, start, end in matches:
            span = doc[start:end]
            match_label = self.nlp.vocab.strings[match_id]

            if match_label.startswith("COLUMN_"):
                column_name = match_label.replace("COLUMN_", "").lower()
                entities["columns"].append({
                    "text": span.text,
                    "column": column_name,
                    "start": start,
                    "end": end,
                })

            elif match_label.startswith("OP_"):
                operator = match_label.replace("OP_", "").lower()
                entities["operators"].append({
                    "text": span.text,
                    "operator": operator,
                    "start": start,
                    "end": end,
                })

            elif match_label.startswith("BOOL_"):
                bool_value = match_label == "BOOL_TRUE"
                entities["values"].append({
                    "text": span.text,
                    "value": bool_value,
                    "type": "boolean",
                    "start": start,
                    "end": end,
                })

            elif match_label.startswith("LOGIC_"):
                logic_type = match_label.replace("LOGIC_", "").lower()
                entities["logic"].append({
                    "text": span.text,
                    "type": logic_type,
                    "start": start,
                    "end": end,
                })

            elif match_label.startswith("INTENT_"):
                intent_type = match_label.replace("INTENT_", "").lower()
                entities["intent"].append({
                    "text": span.text,
                    "type": intent_type,
                    "start": start,
                    "end": end,
                })

            elif match_label.startswith("QUANTIFIER_"):
                quantifier_type = match_label.replace("QUANTIFIER_", "").lower()
                entities["quantifiers"].append({
                    "text": span.text,
                    "type": quantifier_type,
                    "start": start,
                    "end": end,
                })

        # Extract numeric and string values using value extractor
        self.value_extractor.extract_all(doc, entities, cve_spans)

        # Extract values adjacent to multi-value columns
        self._extract_adjacent_values_for_multivalue_columns(doc, entities)

        return entities


    def _extract_adjacent_values_for_multivalue_columns(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """
        Extract values that appear adjacent to multi-value column references.

        For queries like "Show assets with active query maintenance", we need to
        extract "maintenance" as a value for the "active_queries" column.

        Args:
            doc: spaCy processed document
            entities: Dictionary to add extracted values to
        """
        # Get all multi-value column entities
        multivalue_col_entities = [
            col for col in entities.get("columns", [])
            if col["column"] in MULTI_VALUE_COLUMNS or col["column"] in TEXT_LIST_COLUMNS
        ]

        for col_entity in multivalue_col_entities:
            col_end = col_entity["end"]

            # Look for nouns immediately after the column reference
            # Example: "active query maintenance" -> extract "maintenance"
            if col_end < len(doc):
                next_token = doc[col_end]

                # Check if the next token is a noun (potential value)
                if next_token.pos_ in ["NOUN", "PROPN"] and not next_token.is_stop:
                    # Make sure this token isn't already extracted as a value
                    already_extracted = any(
                        v["start"] == next_token.i for v in entities.get("values", [])
                    )

                    if not already_extracted:
                        entities["values"].append({
                            "text": next_token.text,
                            "value": next_token.text,
                            "type": "string",
                            "start": next_token.i,
                            "end": next_token.i + 1,
                        })


