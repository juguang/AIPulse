"""Title-based near-duplicate detection using string similarity.

Three-layer dedup architecture:
    Layer 1: content_hash UNIQUE (DB constraint in raw_items)
    Layer 2: (source_id, guid) UNIQUE (DB constraint in raw_items)
    Layer 3: This module — title-level similarity check via SequenceMatcher

No external ML models required.
"""

from typing import Optional
from difflib import SequenceMatcher


class SemanticDeduplicator:
    """Three-layer dedup Layer 3: title-level near-duplicate detection.

    Compares article titles using Levenshtein-derived similarity (SequenceMatcher).
    Threshold of 0.85 is appropriate for news headline deduplication.
    """

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def encode(self, texts: list[str]) -> list[str]:
        """Return raw titles as-is — this is a simplified interface for compatibility."""
        return texts

    def _similarity(self, a: str, b: str) -> float:
        """Compute string similarity ratio between two titles."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def is_duplicate(self, title: str, existing_titles: list[str]) -> bool:
        """Check if a single title is near-duplicate with any existing title.

        Args:
            title: The article title to check.
            existing_titles: List of titles from previously processed articles.

        Returns:
            True if max similarity exceeds threshold.
        """
        if not existing_titles:
            return False
        for existing in existing_titles:
            if self._similarity(title, existing) > self.threshold:
                return True
        return False

    def find_duplicates_in_batch(
        self,
        items: list[dict],
        existing_titles: list[str],
    ) -> tuple[list[dict], list[str], list[bool]]:
        """Check a batch of new items against existing and intra-batch duplicates.

        Each item is compared against:
            1. All existing titles (previously processed articles)
            2. All non-duplicate items earlier in the same batch

        Args:
            items: List of dicts, each must contain a 'title' key.
            existing_titles: List of titles from existing articles.

        Returns:
            (unique_items, unique_titles, duplicate_mask)
        """
        if not items:
            return [], [], []

        unique_items: list[dict] = []
        unique_titles: list[str] = []
        duplicate_mask: list[bool] = []

        for i, item in enumerate(items):
            title = item.get("title", "")

            # Check against existing (previously processed) titles
            dup = False
            for existing in existing_titles:
                if self._similarity(title, existing) > self.threshold:
                    duplicate_mask.append(True)
                    dup = True
                    break
            if dup:
                continue

            # Check against earlier non-duplicate items in this batch
            for existing in unique_titles:
                if self._similarity(title, existing) > self.threshold:
                    duplicate_mask.append(True)
                    dup = True
                    break
            if dup:
                continue

            unique_items.append(item)
            unique_titles.append(title)
            duplicate_mask.append(False)

        return unique_items, unique_titles, duplicate_mask
