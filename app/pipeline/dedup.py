"""Semantic deduplication using sentence-transformers embeddings.

Three-layer dedup architecture:
    Layer 1: content_hash UNIQUE (DB constraint in raw_items)
    Layer 2: (source_id, guid) UNIQUE (DB constraint in raw_items)
    Layer 3: This module — sentence-transformers 384-dim embeddings + cosine similarity

Uses all-MiniLM-L6-v2 model (~90MB, downloaded on first use via lazy loading).
"""

import numpy as np
from typing import Optional
from sentence_transformers import SentenceTransformer

from app.config import settings as app_settings


class SemanticDeduplicator:
    """Three-layer dedup Layer 3: title-level semantic near-duplicate detection.

    Compares article titles using sentence-transformers embeddings and cosine
    similarity. Threshold of 0.75 is the community standard for news headline
    deduplication.

    Model is lazily loaded (_get_model) to avoid downloading ~90MB on import.
    All encodings use normalize_embeddings=True so dot product = cosine similarity.
    """

    def __init__(self, model_name: str | None = None, threshold: float = 0.75):
        self.model_name = model_name or app_settings.SENTENCE_TRANSFORMERS_MODEL
        self.threshold = threshold
        self._model: Optional[SentenceTransformer] = None

    def _get_model(self) -> SentenceTransformer:
        """Lazy-load the sentence-transformers model (downloaded on first call).

        This prevents the ~90MB model download on module import, deferring it
        until the first actual dedup operation.
        """
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: list[str]) -> np.ndarray:
        """Batch-encode texts into normalized embeddings (dot product = cosine sim)."""
        model = self._get_model()
        return model.encode(texts, normalize_embeddings=True)

    def is_duplicate(self, title: str, existing_embeddings: np.ndarray) -> bool:
        """Check if a single title is semantically duplicate with any existing embedding.

        Args:
            title: The article title to check.
            existing_embeddings: (N, D) matrix of embeddings from previously
                processed articles. Empty array means no comparison possible.

        Returns:
            True if max cosine similarity exceeds threshold.
        """
        if len(existing_embeddings) == 0:
            return False
        emb = self.encode([title])  # shape: (1, 384)
        similarities = np.dot(existing_embeddings, emb.T).flatten()
        return float(np.max(similarities)) > self.threshold

    def find_duplicates_in_batch(
        self,
        items: list[dict],
        existing_embeddings: np.ndarray,
    ) -> tuple[list[dict], np.ndarray, np.ndarray]:
        """Check a batch of new items against existing and intra-batch duplicates.

        Each item is compared against:
            1. All existing embeddings (previously processed articles)
            2. All non-duplicate items earlier in the same batch

        Args:
            items: List of dicts, each must contain a 'title' key.
            existing_embeddings: (N, D) matrix of existing article embeddings.

        Returns:
            (unique_items, unique_embeddings, duplicate_mask)
            - unique_items: Items that passed both dedup checks.
            - unique_embeddings: Embeddings for the unique items (can be
              appended to an external cache).
            - duplicate_mask: Boolean array same length as items; True = duplicate.
        """
        if not items:
            return [], np.array([]), np.array([], dtype=bool)

        titles = [item["title"] for item in items]
        batch_embs = self.encode(titles)  # shape: (N, 384)

        unique_items: list[dict] = []
        unique_embs_list: list[np.ndarray] = []
        duplicate_mask: list[bool] = []

        for i, item in enumerate(items):
            # Check against existing (previously processed) embeddings
            if len(existing_embeddings) > 0:
                sims = np.dot(existing_embeddings, batch_embs[i])
                if float(np.max(sims)) > self.threshold:
                    duplicate_mask.append(True)
                    continue

            # Check against earlier non-duplicate items in this batch
            if len(unique_embs_list) > 0:
                stacked = np.vstack(unique_embs_list)
                sims = np.dot(stacked, batch_embs[i])
                if float(np.max(sims)) > self.threshold:
                    duplicate_mask.append(True)
                    continue

            unique_items.append(item)
            unique_embs_list.append(batch_embs[i])
            duplicate_mask.append(False)

        unique_embs = np.vstack(unique_embs_list) if unique_embs_list else np.array([])
        return (
            unique_items,
            unique_embs,
            np.array(duplicate_mask, dtype=bool),
        )
