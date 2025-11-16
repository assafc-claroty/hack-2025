"""
Constants for NL-to-SQL translation.

This module contains configuration constants used throughout the translator.
"""

# Proximity-based matching
MAX_PROXIMITY_DISTANCE = 5
"""Maximum token distance for proximity-based column-value matching."""

# Dependency path limits
MAX_DEPENDENCY_DEPTH = 100
"""Maximum depth when traversing dependency trees (safety limit)."""

# Limit extraction
MAX_LIMIT_SEARCH_DISTANCE = 3
"""Maximum token distance when searching for LIMIT values."""

