"""Local LXDR-facing request shapes for the bridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .cot_map import CasevacRequest, MaintenanceRequest, MappingResult, SupplyRequest


@dataclass(slots=True, frozen=True)
class LXDRHeader:
    """Represents the minimal header data the bridge will set locally."""

    local_request_id: str
    request_priority: str


@dataclass(slots=True, frozen=True)
class LXDRSegment:
    """Represents one local LXDR segment payload."""

    kind: str
    fields: dict[str, str]


@dataclass(slots=True, frozen=True)
class LXDRRequestContainer:
    """Represents one local LXDR request container."""

    source_uid: str
    header: LXDRHeader
    segment: LXDRSegment


Builder = Callable[[MappingResult], LXDRRequestContainer]


def request_from_mapping(mapping: MappingResult) -> LXDRRequestContainer:
    """Build a local LXDR request container from a normalized bridge mapping."""
    try:
        build = REQUEST_BUILDERS[mapping.bridge_mode]
    except KeyError as exc:
        raise ValueError(f"unsupported bridge mode: {mapping.bridge_mode}") from exc
    return build(mapping)


def _local_request_id(kind: str, source_uid: str) -> str:
    return f"{kind}:{source_uid}"


def _maintenance_request(mapping: MappingResult) -> LXDRRequestContainer:
    req = mapping.normalized_request
    if not isinstance(req, MaintenanceRequest):
        raise ValueError("missing normalized maintenance request")
    return LXDRRequestContainer(
        source_uid=req.source_uid,
        header=LXDRHeader(
            local_request_id=_local_request_id("maintenance", req.source_uid),
            request_priority=req.request_priority,
        ),
        segment=LXDRSegment(
            kind="maintenance",
            fields={
                "maintenance_support": req.maintenance_support,
                "equipment_nomenclature": req.equipment_nomenclature,
                "issue_text": req.issue_text,
            },
        ),
    )


def _supply_request(mapping: MappingResult) -> LXDRRequestContainer:
    req = mapping.normalized_request
    if not isinstance(req, SupplyRequest):
        raise ValueError("missing normalized supply request")
    return LXDRRequestContainer(
        source_uid=req.source_uid,
        header=LXDRHeader(
            local_request_id=_local_request_id("supply", req.source_uid),
            request_priority=req.request_priority,
        ),
        segment=LXDRSegment(
            kind="supply",
            fields={
                "item_nomenclature": req.item_nomenclature,
                "quantity": req.quantity,
                "needed_by": req.needed_by,
            },
        ),
    )


def _casevac_request(mapping: MappingResult) -> LXDRRequestContainer:
    req = mapping.normalized_request
    if not isinstance(req, CasevacRequest):
        raise ValueError("missing normalized casevac request")
    return LXDRRequestContainer(
        source_uid=req.source_uid,
        header=LXDRHeader(
            local_request_id=_local_request_id("casevac", req.source_uid),
            request_priority=req.request_priority,
        ),
        segment=LXDRSegment(
            kind="casevac",
            fields={
                "pickup_location": req.pickup_location,
                "patient_count": req.patient_count,
                "special_equipment": req.special_equipment,
            },
        ),
    )


REQUEST_BUILDERS: dict[str, Builder] = {
    "maintenance": _maintenance_request,
    "supply": _supply_request,
    "casevac": _casevac_request,
}
