"""
Entity recognition for natural language queries using spaCy patterns.
"""

import re
from typing import Any, Dict, List, Set, Tuple, Union

from spacy.matcher import Matcher
from spacy.tokens import Doc, Token

from .schema import (
    COLUMN_SYNONYMS,
    MULTI_VALUE_COLUMNS,
    TEXT_LIST_COLUMNS,
    VALID_COLUMNS,
)


class ExtractionContext:
    """Context object to manage entity extraction state."""

    def __init__(self, entities: Dict[str, List[Dict[str, Any]]]):
        """
        Initialize extraction context.

        Args:
            entities: Dictionary of entities being built
        """
        self.entities = entities
        self.added_columns: Set[Tuple[str, int]] = {
            (e["column"], e["start"]) for e in entities["columns"]
        }
        self.cve_positions: Set[int] = set()

    def add_value(
        self, text: str, value: Any, value_type: str, start: int, end: int
    ) -> None:
        """
        Add a value entity.

        Args:
            text: Original text
            value: Parsed value
            value_type: Type of value (cve, ip_address, mac_address, etc.)
            start: Start token index
            end: End token index
        """
        self.entities["values"].append({
            "text": text,
            "value": value,
            "type": value_type,
            "start": start,
            "end": end,
        })

    def add_column(self, column: str, text: str, position: int) -> bool:
        """
        Add a column entity if not already added.

        Args:
            column: Column name
            text: Display text for the column
            position: Token position

        Returns:
            True if column was added, False if it already existed
        """
        if column not in VALID_COLUMNS:
            return False

        if (column, position) in self.added_columns:
            return False

        self.entities["columns"].append({
            "text": text,
            "column": column,
            "start": position,
            "end": position + 1,
        })
        self.added_columns.add((column, position))
        return True


class EntityRecognizer:
    """Recognizes entities in natural language queries for SQL translation."""

    # Compile regex patterns once at class level for performance
    CVE_PATTERN = re.compile(r'^CVE-\d{4}-\d{4,}$', re.IGNORECASE)
    MAC_PATTERN = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')

    def __init__(self, nlp: Any) -> None:
        """
        Initialize the entity recognizer.

        Args:
            nlp: spaCy language model
        """
        self.nlp = nlp
        self.matcher = Matcher(nlp.vocab)
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
        cve_spans = self._find_cve_spans(doc)

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

        # Extract numeric and string values
        self._extract_values(doc, entities, cve_spans)

        # Extract values adjacent to multi-value columns
        self._extract_adjacent_values_for_multivalue_columns(doc, entities)

        return entities

    def _find_cve_spans(self, doc: Doc) -> List[Tuple[int, int, str]]:
        """
        Find multi-token CVE identifiers in the document.

        CVE identifiers like "CVE-2017-12819" are often tokenized as multiple tokens.
        SpaCy typically tokenizes as: "CVE-2017", "-", "12819"

        Args:
            doc: spaCy processed document

        Returns:
            List of (start_idx, end_idx, cve_text) tuples
        """
        cve_spans = []
        i = 0
        while i < len(doc):
            # Look for CVE pattern: "CVE-YYYY", "-", "NNNNN"
            if i + 2 < len(doc):
                # Check if first token starts with CVE and contains a dash and year
                if doc[i].text.startswith("CVE-") and doc[i+1].text == "-":
                    # Combine the three tokens
                    combined = doc[i].text + doc[i+1].text + doc[i+2].text

                    # Check if it matches CVE pattern
                    if self.CVE_PATTERN.match(combined):
                        cve_spans.append((i, i + 3, combined))
                        i += 3
                        continue

            # Also check for single-token CVE (less common but possible)
            if self.CVE_PATTERN.match(doc[i].text):
                cve_spans.append((i, i + 1, doc[i].text))
                i += 1
                continue

            i += 1

        return cve_spans

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

    def _extract_values(
        self,
        doc: Doc,
        entities: Dict[str, List[Dict[str, Any]]],
        cve_spans: Union[List[Tuple[int, int, str]], None] = None
    ) -> None:
        """
        Extract numeric and string literal values from the document.

        Uses advanced pattern matching to identify:
        - Numbers (integers and floats)
        - IP addresses (IPv4 and partial patterns)
        - CVE identifiers (CVE-YYYY-NNNNN)
        - Quoted strings
        - MAC addresses
        - Vendor/model names

        Args:
            doc: spaCy processed document
            entities: Dictionary to add extracted values to
            cve_spans: Pre-identified multi-token CVE spans
        """
        context = ExtractionContext(entities)

        # Process multi-token CVE spans first
        self._process_cve_spans(cve_spans, context)

        # Extract values token by token
        for token in doc:
            if token.i in context.cve_positions:
                continue

            # Try each extraction method in priority order
            # Each method returns True if it extracted a value
            if self._extract_cve_value(token, context):
                continue
            if self._extract_ip_value(token, context):
                continue
            if self._extract_mac_value(token, context):
                continue
            if self._extract_numeric_value(token, context):
                continue
            if self._extract_quoted_string_value(token, context):
                continue
            if self._extract_proper_noun_value(token, context):
                continue
            if self._extract_identifier_noun_value(token, context):
                continue

    def _process_cve_spans(
        self,
        cve_spans: Union[List[Tuple[int, int, str]], None],
        context: ExtractionContext
    ) -> None:
        """
        Process pre-identified multi-token CVE spans.

        Args:
            cve_spans: List of (start, end, cve_text) tuples
            context: Extraction context
        """
        if not cve_spans:
            return

        for start, end, cve_text in cve_spans:
            # Mark positions as part of CVE
            for pos in range(start, end):
                context.cve_positions.add(pos)

            # Add the CVE as a value
            context.add_value(cve_text, cve_text, "cve", start, end)

            # Add CVE column reference
            context.add_column("CVE", "CVE", start)

    def _extract_cve_value(self, token: Token, context: ExtractionContext) -> bool:
        """
        Extract CVE identifier from token.

        Args:
            token: Token to check
            context: Extraction context

        Returns:
            True if CVE was extracted
        """
        if not self._is_cve_identifier(token.text):
            return False

        context.add_value(token.text, token.text, "cve", token.i, token.i + 1)
        context.add_column("CVE", "CVE", token.i)
        return True

    def _extract_ip_value(self, token: Token, context: ExtractionContext) -> bool:
        """
        Extract IP address from token.

        Args:
            token: Token to check
            context: Extraction context

        Returns:
            True if IP was extracted
        """
        if not self._is_ip_address(token.text):
            return False

        context.add_value(token.text, token.text, "ip_address", token.i, token.i + 1)
        context.add_column("ipv4", "ip", token.i)
        return True

    def _extract_mac_value(self, token: Token, context: ExtractionContext) -> bool:
        """
        Extract MAC address from token.

        Args:
            token: Token to check
            context: Extraction context

        Returns:
            True if MAC was extracted
        """
        if not self._is_mac_address(token.text):
            return False

        context.add_value(token.text, token.text, "mac_address", token.i, token.i + 1)
        return True

    def _extract_numeric_value(self, token: Token, context: ExtractionContext) -> bool:
        """
        Extract numeric value (integer or float) from token.

        Args:
            token: Token to check
            context: Extraction context

        Returns:
            True if number was extracted
        """
        if not (token.like_num or token.pos_ == "NUM"):
            return False

        # Try integer first
        try:
            int_value = int(token.text)
            context.add_value(token.text, int_value, "integer", token.i, token.i + 1)
            return True
        except ValueError:
            pass

        # Try float
        try:
            float_value = float(token.text)
            context.add_value(token.text, float_value, "float", token.i, token.i + 1)
            return True
        except ValueError:
            pass

        return False

    def _extract_quoted_string_value(
        self, token: Token, context: ExtractionContext
    ) -> bool:
        """
        Extract quoted string from token.

        Args:
            token: Token to check
            context: Extraction context

        Returns:
            True if quoted string was extracted
        """
        if not (token.text.startswith('"') or token.text.startswith("'")):
            return False

        unquoted = token.text.strip('"\'')
        context.add_value(token.text, unquoted, "string", token.i, token.i + 1)
        return True

    def _extract_proper_noun_value(
        self, token: Token, context: ExtractionContext
    ) -> bool:
        """
        Extract proper noun (vendor name or string) from token.

        Args:
            token: Token to check
            context: Extraction context

        Returns:
            True if proper noun was extracted
        """
        if token.pos_ != "PROPN":
            return False

        value_type = "vendor" if self._is_vendor_or_model(token.text) else "string"
        context.add_value(token.text, token.text, value_type, token.i, token.i + 1)
        return True

    def _extract_identifier_noun_value(
        self, token: Token, context: ExtractionContext
    ) -> bool:
        """
        Extract noun that looks like an identifier (e.g., server01, device123).

        Args:
            token: Token to check
            context: Extraction context

        Returns:
            True if identifier noun was extracted
        """
        if not self._is_identifier_noun(token):
            return False

        context.add_value(token.text, token.text, "string", token.i, token.i + 1)
        return True

    def _is_identifier_noun(self, token: Token) -> bool:
        """
        Check if token is a noun that looks like an identifier.

        Args:
            token: Token to check

        Returns:
            True if token is an identifier noun
        """
        return token.pos_ == "NOUN" and any(c.isdigit() for c in token.text)

    def _is_cve_identifier(self, text: str) -> bool:
        """
        Check if text is a CVE identifier.

        Pattern: CVE-YYYY-NNNNN (e.g., CVE-2025-10501)

        Args:
            text: Text to check

        Returns:
            True if text matches CVE pattern
        """
        return bool(self.CVE_PATTERN.match(text))

    def _is_ip_address(self, text: str) -> bool:
        """
        Check if text looks like an IP address or partial IP pattern.

        Supports:
        - Full IPv4: 192.168.1.1
        - Partial patterns: 10.89.* or 10.89

        Args:
            text: Text to check

        Returns:
            True if text matches IP pattern
        """
        if not isinstance(text, str):
            return False

        parts = text.split('.')

        # Check for full IP address
        if len(parts) == 4:
            try:
                return all(0 <= int(part) <= 255 for part in parts if part != '*')
            except ValueError:
                return False

        # Check for partial IP (e.g., "10.89")
        if len(parts) >= 2:
            try:
                return all(0 <= int(part) <= 255 for part in parts if part.isdigit())
            except ValueError:
                return False

        return False

    def _is_mac_address(self, text: str) -> bool:
        """
        Check if text looks like a MAC address.

        Pattern: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX

        Args:
            text: Text to check

        Returns:
            True if text matches MAC address pattern
        """
        return bool(self.MAC_PATTERN.match(text))

    def _is_vendor_or_model(self, text: str) -> bool:
        """
        Check if text is a known vendor or model name.

        Args:
            text: Text to check

        Returns:
            True if text is a known vendor/model
        """
        known_vendors = {
            "siemens", "rockwell", "schneider", "abb", "ge", "honeywell",
            "yokogawa", "emerson", "cisco", "dell", "hp", "lenovo",
            "microsoft", "linux", "windows", "ubuntu", "debian", "redhat",
            "plc", "scada", "hmi", "dcs"
        }
        return text.lower() in known_vendors

