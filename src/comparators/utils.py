from __future__ import annotations

from typing import Iterable


def tokens_to_string(tokens: Iterable[str]) -> str:
    """Join tokens into a single normalized string."""
    return " ".join(tok for tok in tokens if tok).strip()
