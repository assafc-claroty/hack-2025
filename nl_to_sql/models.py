"""
Data models for natural language to SQL translation.

This module defines dataclasses that replace primitive dictionaries,
providing type safety and better IDE support.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional

from spacy.tokens import Doc


@dataclass
class ColumnEntity:
    """Represents a recognized column entity."""

    text: str
    column: str
    start: int
    end: int


@dataclass
class ValueEntity:
    """Represents a recognized value entity."""

    text: str
    value: Any
    type: str  # 'integer', 'string', 'cve', 'ip_address', etc.
    start: int
    end: int


@dataclass
class OperatorEntity:
    """Represents a recognized operator entity."""

    text: str
    operator: str  # 'equals', 'not_equals', 'greater', 'less', 'like', 'in'
    start: int
    end: int


@dataclass
class LogicEntity:
    """Represents a logical connector entity."""

    text: str
    type: str  # 'and', 'or'
    start: int
    end: int


@dataclass
class IntentEntity:
    """Represents an intent entity."""

    text: str
    type: str  # 'show', 'count', 'exists'
    start: int
    end: int


@dataclass
class QuantifierEntity:
    """Represents a quantifier entity."""

    text: str
    type: str  # 'all', 'any'
    start: int
    end: int


@dataclass
class RecognizedEntities:
    """Collection of recognized entities."""

    columns: List[ColumnEntity] = field(default_factory=list)
    values: List[ValueEntity] = field(default_factory=list)
    operators: List[OperatorEntity] = field(default_factory=list)
    logic: List[LogicEntity] = field(default_factory=list)
    intent: List[IntentEntity] = field(default_factory=list)
    quantifiers: List[QuantifierEntity] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary format for backward compatibility."""
        return {
            "columns": [
                {
                    "text": c.text,
                    "column": c.column,
                    "start": c.start,
                    "end": c.end,
                }
                for c in self.columns
            ],
            "values": [
                {
                    "text": v.text,
                    "value": v.value,
                    "type": v.type,
                    "start": v.start,
                    "end": v.end,
                }
                for v in self.values
            ],
            "operators": [
                {"text": o.text, "operator": o.operator, "start": o.start, "end": o.end}
                for o in self.operators
            ],
            "logic": [
                {"text": l.text, "type": l.type, "start": l.start, "end": l.end}
                for l in self.logic
            ],
            "intent": [
                {"text": i.text, "type": i.type, "start": i.start, "end": i.end}
                for i in self.intent
            ],
            "quantifiers": [
                {"text": q.text, "type": q.type, "start": q.start, "end": q.end}
                for q in self.quantifiers
            ],
        }


@dataclass
class WhereCondition:
    """Represents a WHERE clause condition."""

    column: str
    operator: str
    value: Any
    logic: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format for backward compatibility."""
        result = {
            "column": self.column,
            "operator": self.operator,
            "value": self.value,
        }
        if self.logic:
            result["logic"] = self.logic
        return result


@dataclass
class OrderByClause:
    """Represents an ORDER BY clause."""

    column: str
    direction: str  # 'ASC' or 'DESC'

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {"column": self.column, "direction": self.direction}


@dataclass
class SQLQuery:
    """Represents a SQL query structure."""

    table: str
    select: List[str]
    where: List[WhereCondition] = field(default_factory=list)
    order_by: List[OrderByClause] = field(default_factory=list)
    limit: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format for backward compatibility."""
        return {
            "table": self.table,
            "select": self.select,
            "where": [c.to_dict() for c in self.where],
            "order_by": [o.to_dict() for o in self.order_by],
            "limit": self.limit,
        }


@dataclass
class Intent:
    """Represents query intent."""

    type: str  # 'select', 'count', 'exists'
    confidence: float = 1.0
    aggregation: Optional[str] = None
    select_columns: Optional[List[str]] = None
    limit: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format for backward compatibility."""
        result = {"type": self.type, "confidence": self.confidence}
        if self.aggregation:
            result["aggregation"] = self.aggregation
        if self.select_columns:
            result["select_columns"] = self.select_columns
        if self.limit is not None:
            result["limit"] = self.limit
        return result


@dataclass
class ParsedQuery:
    """Represents a fully parsed query."""

    doc: Doc
    entities: RecognizedEntities
    conditions: List[WhereCondition]
    select: List[str]
    order_by: List[OrderByClause]
    limit: Optional[int]

    def to_dict(self) -> dict:
        """Convert to dictionary format for backward compatibility."""
        return {
            "doc": self.doc,
            "entities": self.entities.to_dict(),
            "conditions": [c.to_dict() for c in self.conditions],
            "select": self.select,
            "order_by": [o.to_dict() for o in self.order_by],
            "limit": self.limit,
        }

