"""
Value extraction using Chain of Responsibility pattern.

This module refactors the god function EntityRecognizer._extract_values()
into smaller, focused extractor classes.
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple

from spacy.tokens import Doc, Token

# Constants for CVE pattern matching
CVE_TOKEN_LOOKAHEAD = 2  # CVE pattern spans 3 tokens: "CVE-2017", "-", "12819"
CVE_PATTERN_PARTS = 3  # Total tokens in multi-token CVE pattern

# Constants for IP address validation
IPV4_OCTET_COUNT = 4  # Full IPv4 address has 4 octets
IPV4_MIN_OCTETS = 2  # Minimum octets for partial IP pattern (e.g., "10.89")


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

        Example:
            >>> context.add_value("192.168.1.1", "192.168.1.1", "ip_address", 5, 6)
            >>> context.add_value("54", 54, "integer", 3, 4)
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

        Example:
            >>> context.add_column("site", "site", 2)
            True
            >>> context.add_column("site", "site", 2)  # Duplicate
            False
        """
        from .schema import VALID_COLUMNS

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

    def should_skip_token(self, token: Token) -> bool:
        """
        Check if token should be skipped.

        Args:
            token: Token to check

        Returns:
            True if token should be skipped

        Example:
            >>> context.should_skip_token(token)  # Returns True if part of CVE
            False
        """
        return token.i in self.cve_positions

    def mark_cve_positions(self, start: int, end: int) -> None:
        """
        Mark token positions as part of CVE.

        Args:
            start: Start position
            end: End position
        """
        for pos in range(start, end):
            self.cve_positions.add(pos)


class BaseValueExtractor(ABC):
    """Base class for value extractors."""

    @abstractmethod
    def extract(self, token: Token, context: ExtractionContext) -> bool:
        """
        Try to extract a value from the token.

        Args:
            token: Token to check
            context: Extraction context

        Returns:
            True if extraction succeeded, False otherwise
        """
        pass


class CVEValueExtractor(BaseValueExtractor):
    """Extracts CVE identifiers."""

    CVE_PATTERN = re.compile(r'^CVE-\d{4}-\d{4,}$', re.IGNORECASE)

    def extract(self, token: Token, context: ExtractionContext) -> bool:
        """Extract CVE identifier from token."""
        if not self._is_cve_identifier(token.text):
            return False

        context.add_value(token.text, token.text, "cve", token.i, token.i + 1)
        context.add_column("CVE", "CVE", token.i)
        return True

    def _is_cve_identifier(self, text: str) -> bool:
        """Check if text is a CVE identifier."""
        return bool(self.CVE_PATTERN.match(text))


class IPValueExtractor(BaseValueExtractor):
    """Extracts IP addresses."""

    def extract(self, token: Token, context: ExtractionContext) -> bool:
        """Extract IP address from token."""
        ip_value, is_prefix = self._parse_ip_address(token.text)
        if not ip_value:
            return False

        # Store whether this is a prefix for later operator selection
        value_type = "ip_prefix" if is_prefix else "ip_address"
        context.add_value(token.text, ip_value, value_type, token.i, token.i + 1)
        context.add_column("ipv4", "ip", token.i)
        return True

    def _parse_ip_address(self, text: str) -> tuple:
        """
        Parse IP address and determine if it's a prefix pattern.

        Returns:
            Tuple of (ip_value, is_prefix)
        """
        if not isinstance(text, str):
            return (None, False)

        parts = text.split('.')

        # Check for full IP address
        if len(parts) == IPV4_OCTET_COUNT:
            try:
                if all(0 <= int(part) <= 255 for part in parts if part != '*'):
                    return (text, False)
            except ValueError:
                return (None, False)

        # Check for partial IP (e.g., "10.89")
        if len(parts) >= IPV4_MIN_OCTETS:
            try:
                if all(0 <= int(part) <= 255 for part in parts if part.isdigit()):
                    # This is a prefix pattern
                    return (text, True)
            except ValueError:
                return (None, False)

        return (None, False)
    
    def _is_ip_address(self, text: str) -> bool:
        """
        Check if text looks like an IP address or partial IP pattern.

        Supports:
        - Full IPv4: 192.168.1.1
        - Partial patterns: 10.89.* or 10.89
        """
        ip_value, _ = self._parse_ip_address(text)
        return ip_value is not None


class MACValueExtractor(BaseValueExtractor):
    """Extracts MAC addresses."""

    MAC_PATTERN = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')

    def extract(self, token: Token, context: ExtractionContext) -> bool:
        """Extract MAC address from token."""
        if not self._is_mac_address(token.text):
            return False

        context.add_value(token.text, token.text, "mac_address", token.i, token.i + 1)
        return True

    def _is_mac_address(self, text: str) -> bool:
        """Check if text looks like a MAC address."""
        return bool(self.MAC_PATTERN.match(text))


class NumericValueExtractor(BaseValueExtractor):
    """Extracts numeric values (integers and floats)."""
    
    # Words that look numeric but shouldn't be extracted
    SKIP_TOKENS = {"a", "i", "s", "o"}  # Single letters that might be parsed as hex

    def extract(self, token: Token, context: ExtractionContext) -> bool:
        """Extract numeric value from token."""
        if not (token.like_num or token.pos_ == "NUM"):
            return False
        
        # Skip single letter tokens that aren't actually numbers
        if token.lower_ in self.SKIP_TOKENS:
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


class QuotedStringValueExtractor(BaseValueExtractor):
    """Extracts quoted strings."""

    def extract(self, token: Token, context: ExtractionContext) -> bool:
        """Extract quoted string from token."""
        if not (token.text.startswith('"') or token.text.startswith("'")):
            return False

        unquoted = token.text.strip('"\'')
        context.add_value(token.text, unquoted, "string", token.i, token.i + 1)
        return True


class ProperNounValueExtractor(BaseValueExtractor):
    """Extracts proper nouns (vendor names or strings)."""

    KNOWN_VENDORS = {
        "siemens", "rockwell", "schneider", "abb", "ge", "honeywell",
        "yokogawa", "emerson", "cisco", "dell", "hp", "lenovo",
        "microsoft", "linux", "windows", "ubuntu", "debian", "redhat",
        "plc", "scada", "hmi", "dcs"
    }
    
    # Words that should not be extracted as values
    STOP_WORDS = {
        "ip", "cve", "site", "asset", "assets", "vulnerability", "vulnerabilities",
        "information", "status", "devices", "device", "network", "system", "systems"
    }

    def extract(self, token: Token, context: ExtractionContext) -> bool:
        """Extract proper noun from token."""
        if token.pos_ != "PROPN":
            return False
        
        # Skip stop words
        if token.lower_ in self.STOP_WORDS:
            return False

        value_type = "vendor" if self._is_vendor_or_model(token.text) else "string"
        context.add_value(token.text, token.text, value_type, token.i, token.i + 1)
        return True

    def _is_vendor_or_model(self, text: str) -> bool:
        """Check if text is a known vendor or model name."""
        return text.lower() in self.KNOWN_VENDORS


class IdentifierNounValueExtractor(BaseValueExtractor):
    """Extracts nouns that look like identifiers (e.g., server01, device123)."""

    def extract(self, token: Token, context: ExtractionContext) -> bool:
        """Extract identifier noun from token."""
        if not self._is_identifier_noun(token):
            return False

        context.add_value(token.text, token.text, "string", token.i, token.i + 1)
        return True

    def _is_identifier_noun(self, token: Token) -> bool:
        """Check if token is a noun that looks like an identifier."""
        return token.pos_ == "NOUN" and any(c.isdigit() for c in token.text)


class CVESpanProcessor:
    """Processes multi-token CVE spans."""

    CVE_PATTERN = re.compile(r'^CVE-\d{4}-\d{4,}$', re.IGNORECASE)

    def process(
        self, cve_spans: List[Tuple[int, int, str]], context: ExtractionContext
    ) -> None:
        """
        Process pre-identified multi-token CVE spans.

        Args:
            cve_spans: List of (start, end, cve_text) tuples
            context: Extraction context
        """
        for start, end, cve_text in cve_spans:
            # Mark positions as part of CVE
            context.mark_cve_positions(start, end)

            # Add the CVE as a value
            context.add_value(cve_text, cve_text, "cve", start, end)

            # Add CVE column reference
            context.add_column("CVE", "CVE", start)

    def find_cve_spans(self, doc: Doc) -> List[Tuple[int, int, str]]:
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
            if i + CVE_TOKEN_LOOKAHEAD < len(doc):
                # Check if first token starts with CVE and contains a dash and year
                if doc[i].text.startswith("CVE-") and doc[i + 1].text == "-":
                    # Combine the three tokens
                    combined = doc[i].text + doc[i + 1].text + doc[i + 2].text

                    # Check if it matches CVE pattern
                    if self.CVE_PATTERN.match(combined):
                        cve_spans.append((i, i + CVE_PATTERN_PARTS, combined))
                        i += CVE_PATTERN_PARTS
                        continue

            # Also check for single-token CVE (less common but possible)
            if self.CVE_PATTERN.match(doc[i].text):
                cve_spans.append((i, i + 1, doc[i].text))
                i += 1
                continue

            i += 1

        return cve_spans


class ValueExtractor:
    """Extracts values using chain of responsibility pattern."""

    def __init__(self):
        """Initialize value extractor with all extraction strategies."""
        self.extractors = [
            CVEValueExtractor(),
            IPValueExtractor(),
            MACValueExtractor(),
            NumericValueExtractor(),
            QuotedStringValueExtractor(),
            ProperNounValueExtractor(),
            IdentifierNounValueExtractor(),
        ]
        self.cve_span_processor = CVESpanProcessor()

    def extract_all(
        self,
        doc: Doc,
        entities: Dict[str, List[Dict[str, Any]]],
        cve_spans: Optional[List[Tuple[int, int, str]]] = None,
    ) -> None:
        """
        Extract all values from document.

        Args:
            doc: spaCy processed document
            entities: Dictionary to add extracted values to
            cve_spans: Pre-identified multi-token CVE spans
        """
        context = ExtractionContext(entities)

        # Process CVE spans separately (they're multi-token)
        if cve_spans:
            self.cve_span_processor.process(cve_spans, context)

        # Process each token through the chain
        for token in doc:
            if context.should_skip_token(token):
                continue

            # Chain of responsibility: first extractor that succeeds stops the chain
            for extractor in self.extractors:
                if extractor.extract(token, context):
                    break

    def find_cve_spans(self, doc: Doc) -> List[Tuple[int, int, str]]:
        """
        Find multi-token CVE identifiers in the document.

        Args:
            doc: spaCy processed document

        Returns:
            List of (start_idx, end_idx, cve_text) tuples
        """
        return self.cve_span_processor.find_cve_spans(doc)

