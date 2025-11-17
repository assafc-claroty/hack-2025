"""
Utility classes for dependency tree analysis.

This module provides utilities for working with spaCy dependency trees,
extracted from the QueryParser to improve single responsibility.
"""

import logging
from typing import List, Optional

from spacy.tokens import Token

from .constants import MAX_DEPENDENCY_DEPTH

logger = logging.getLogger(__name__)


class DependencyPathFinder:
    """Finds dependency paths between tokens in a parse tree."""

    def __init__(self, max_depth: int = MAX_DEPENDENCY_DEPTH):
        """
        Initialize the path finder.

        Args:
            max_depth: Maximum depth when traversing dependency trees
        """
        self.max_depth = max_depth

    def find_path(self, token1: Token, token2: Token) -> List[Token]:
        """
        Get the dependency path between two tokens.

        Args:
            token1: First token
            token2: Second token

        Returns:
            List of tokens in the path
        """
        lca = self._find_lowest_common_ancestor(token1, token2)
        if not lca:
            return []

        path_to_lca = self._build_path_to_ancestor(token1, lca)
        path_from_lca = self._build_path_to_ancestor(token2, lca)

        return path_to_lca + [lca] + list(reversed(path_from_lca))

    def _find_lowest_common_ancestor(
        self, token1: Token, token2: Token
    ) -> Optional[Token]:
        """
        Find the lowest common ancestor of two tokens.

        Args:
            token1: First token
            token2: Second token

        Returns:
            Lowest common ancestor token or None
        """
        ancestors1 = set([token1] + list(token1.ancestors))
        ancestors2 = set([token2] + list(token2.ancestors))

        common = ancestors1 & ancestors2
        if not common:
            return None

        try:
            return min(common, key=lambda t: t.i)
        except ValueError:
            # No common ancestors found (empty set)
            return None
        except AttributeError as e:
            # Token missing 'i' attribute - should never happen with spaCy tokens
            logger.warning(f"Unexpected token structure in dependency path: {e}")
            return None

    def _build_path_to_ancestor(self, token: Token, ancestor: Token) -> List[Token]:
        """
        Build path from token to ancestor with safety limit.

        Args:
            token: Starting token
            ancestor: Target ancestor token

        Returns:
            List of tokens in the path (excluding ancestor)
        """
        path = []
        current = token
        depth = 0

        while (
            current != ancestor and current is not None and depth < self.max_depth
        ):
            path.append(current)

            # Check for ROOT token (where head == self)
            if current.head == current:
                break

            current = current.head
            depth += 1

        return path

