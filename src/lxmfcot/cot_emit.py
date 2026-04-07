"""TAK/CoT status emission helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class StatusEvent:
    """Represents a bridge status outcome for later CoT emission."""

    status: str
    detail: str

