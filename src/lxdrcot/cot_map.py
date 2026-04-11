"""CoT to LXDR mapping contracts."""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_BRIDGE_MODES = (
    "maintenance",
    "supply",
    "casevac",
)


@dataclass(slots=True, frozen=True)
class MappingResult:
    """Represents the result of a CoT classification step."""

    bridge_mode: str
    source_uid: str
    raw_payload: bytes


def is_supported_bridge_mode(value: str) -> bool:
    """Report whether the requested bridge mode is supported."""
    return value in SUPPORTED_BRIDGE_MODES

