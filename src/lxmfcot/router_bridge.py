"""Bridge handoff into an LXDR router."""

from __future__ import annotations

from dataclasses import dataclass

from .cot_emit import StatusEvent
from .cot_map import MappingResult


@dataclass(slots=True, frozen=True)
class BridgeOutcome:
    """Represents the local bridge outcome."""

    accepted: bool
    status_event: StatusEvent


def accept_mapping(mapping: MappingResult) -> BridgeOutcome:
    """Accept a classified mapping into the local bridge flow."""
    return BridgeOutcome(
        accepted=True,
        status_event=StatusEvent(
            status="accepted",
            detail=f"{mapping.bridge_mode}:{mapping.source_uid}",
        ),
    )

