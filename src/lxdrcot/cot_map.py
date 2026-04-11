"""CoT to LXDR mapping contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from xml.etree.ElementTree import Element


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
    normalized_request: Any | None = None


@dataclass(slots=True, frozen=True)
class MaintenanceRequest:
    """Normalized maintenance request extracted from CoT."""

    source_uid: str
    request_priority: str
    maintenance_support: str
    equipment_nomenclature: str
    issue_text: str


def _maintenance_detail_from_event(root: Element) -> MaintenanceRequest:
    """Extract the strict maintenance detail contract from a CoT event."""
    detail = root.find("detail")
    if detail is None:
        raise ValueError("missing CoT detail")

    contract = detail.find("lxdrcot")
    if contract is None:
        raise ValueError("missing lxdrcot detail")

    request_priority = contract.attrib.get("request_priority", "").strip()
    if not request_priority:
        raise ValueError("missing maintenance request_priority")

    maintenance_support = contract.attrib.get("maintenance_support", "").strip()
    if not maintenance_support:
        raise ValueError("missing maintenance maintenance_support")

    equipment_nomenclature = contract.attrib.get("equipment_nomenclature", "").strip()
    if not equipment_nomenclature:
        raise ValueError("missing maintenance equipment_nomenclature")

    issue_text = contract.attrib.get("issue_text", "").strip()
    if not issue_text:
        raise ValueError("missing maintenance issue_text")

    return MaintenanceRequest(
        source_uid=root.attrib["uid"].strip(),
        request_priority=request_priority,
        maintenance_support=maintenance_support,
        equipment_nomenclature=equipment_nomenclature,
        issue_text=issue_text,
    )


def is_supported_bridge_mode(value: str) -> bool:
    """Report whether the requested bridge mode is supported."""
    return value in SUPPORTED_BRIDGE_MODES


def classify_event_type(event_type: str) -> str:
    """Map a CoT event type to a supported bridge mode."""
    event_type = event_type.strip()
    if event_type == "b-m-p-s-p-lxdr-maintenance":
        return "maintenance"
    if event_type == "b-m-p-s-p-lxdr-supply":
        return "supply"
    if event_type == "b-m-p-s-p-lxdr-casevac":
        return "casevac"
    raise ValueError(f"unsupported CoT event type: {event_type}")


def mapping_from_event(root: Element, raw_payload: bytes) -> MappingResult:
    """Build a mapping result from a parsed CoT event element."""
    source_uid = root.attrib.get("uid", "").strip()
    if not source_uid:
        raise ValueError("missing CoT uid")

    event_type = root.attrib.get("type", "").strip()
    if not event_type:
        raise ValueError("missing CoT type")

    bridge_mode = classify_event_type(event_type)
    normalized_request = None
    if bridge_mode == "maintenance":
        normalized_request = _maintenance_detail_from_event(root)

    return MappingResult(
        bridge_mode=bridge_mode,
        source_uid=source_uid,
        raw_payload=raw_payload,
        normalized_request=normalized_request,
    )
