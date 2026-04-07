"""PyTAK ingest worker definitions."""

from __future__ import annotations

from .cot_map import MappingResult


def classify_payload(data: bytes) -> MappingResult:
    """Classify raw payload bytes into the current placeholder bridge mode."""
    # v0 keeps the ingest contract narrow. Real CoT parsing lands next.
    return MappingResult(
        bridge_mode="maintenance",
        source_uid="pending",
        raw_payload=data,
    )

