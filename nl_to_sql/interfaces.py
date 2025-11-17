"""
Abstract interfaces for dependency inversion principle.

This module defines the core interfaces that allow for loose coupling
and easy testing through dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from spacy.tokens import Doc, Token


class NLPProcessor(ABC):
    """Abstract interface for NLP processing."""

    @abstractmethod
    def process(self, text: str) -> Doc:
        """
        Process text and return spaCy document.

        Args:
            text: Input text to process

        Returns:
            Processed spaCy Doc object
        """
        pass


class EntityRecognizerInterface(ABC):
    """Abstract interface for entity recognition."""

    @abstractmethod
    def recognize(self, doc: Doc) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recognize entities in document.

        Args:
            doc: spaCy processed document

        Returns:
            Dictionary of recognized entities by category
        """
        pass


class IntentClassifierInterface(ABC):
    """Abstract interface for intent classification."""

    @abstractmethod
    def classify(
        self, doc: Doc, entities: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Classify the intent of a query.

        Args:
            doc: spaCy processed document
            entities: Recognized entities

        Returns:
            Dictionary with intent information
        """
        pass


class QueryBuilderInterface(ABC):
    """Abstract interface for query building."""

    @abstractmethod
    def build(
        self, parsed_data: Dict[str, Any], intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build a JSON representation of a SQL query.

        Args:
            parsed_data: Parsed query components
            intent: Intent classification result

        Returns:
            JSON representation of the SQL query
        """
        pass

    @abstractmethod
    def to_sql(self, query_json: Dict[str, Any]) -> str:
        """
        Convert JSON query representation to SQL string.

        Args:
            query_json: JSON representation of query

        Returns:
            SQL query string
        """
        pass


class QueryParserInterface(ABC):
    """Abstract interface for query parsing."""

    @abstractmethod
    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query.

        Args:
            query: Natural language query string

        Returns:
            Dictionary containing parsed components
        """
        pass

