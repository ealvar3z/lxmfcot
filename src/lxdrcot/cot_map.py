"""CoT to LXDR mapping contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
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


@dataclass(slots=True, frozen=True)
class SupplyRequest:
    """Normalized supply request extracted from CoT."""

    source_uid: str
    request_priority: str
    item_nomenclature: str
    quantity: str
    needed_by: str


@dataclass(slots=True, frozen=True)
class CasevacRequest:
    """Normalized CASEVAC request extracted from CoT."""

    source_uid: str
    request_priority: str
    pickup_location: str
    patient_count: str
    special_equipment: str


NormalizedRequest = MaintenanceRequest | SupplyRequest | CasevacRequest
Extractor = Callable[[Element], NormalizedRequest]


def _require_contract(root: Element) -> Element:
    """Return the required lxdrcot detail contract element."""
    detail = root.find("detail")
    if detail is None:
        raise ValueError("missing CoT detail")

    contract = detail.find("lxdrcot")
    if contract is None:
        raise ValueError("missing lxdrcot detail")

    return contract


def _require_attr(contract: Element, name: str, context: str) -> str:
    """Return a required attribute from the contract element."""
    value = contract.attrib.get(name, "").strip()
    if not value:
        raise ValueError(f"missing {context} {name}")
    return value


def _maintenance_detail_from_event(root: Element) -> MaintenanceRequest:
    """Extract the strict maintenance detail contract from a CoT event."""
    contract = _require_contract(root)

    request_priority = _require_attr(contract, "request_priority", "maintenance")
    maintenance_support = _require_attr(contract, "maintenance_support", "maintenance")
    equipment_nomenclature = _require_attr(
        contract, "equipment_nomenclature", "maintenance"
    )
    issue_text = _require_attr(contract, "issue_text", "maintenance")

    return MaintenanceRequest(
        source_uid=root.attrib["uid"].strip(),
        request_priority=request_priority,
        maintenance_support=maintenance_support,
        equipment_nomenclature=equipment_nomenclature,
        issue_text=issue_text,
    )


def _supply_detail_from_event(root: Element) -> SupplyRequest:
    """Extract the strict supply detail contract from a CoT event."""
    contract = _require_contract(root)

    request_priority = _require_attr(contract, "request_priority", "supply")
    item_nomenclature = _require_attr(contract, "item_nomenclature", "supply")
    quantity = _require_attr(contract, "quantity", "supply")
    needed_by = _require_attr(contract, "needed_by", "supply")

    return SupplyRequest(
        source_uid=root.attrib["uid"].strip(),
        request_priority=request_priority,
        item_nomenclature=item_nomenclature,
        quantity=quantity,
        needed_by=needed_by,
    )


def _casevac_detail_from_event(root: Element) -> CasevacRequest:
    """Extract the strict CASEVAC detail contract from a CoT event."""
    contract = _require_contract(root)

    request_priority = _require_attr(contract, "request_priority", "casevac")
    pickup_location = _require_attr(contract, "pickup_location", "casevac")
    patient_count = _require_attr(contract, "patient_count", "casevac")
    special_equipment = _require_attr(contract, "special_equipment", "casevac")

    return CasevacRequest(
        source_uid=root.attrib["uid"].strip(),
        request_priority=request_priority,
        pickup_location=pickup_location,
        patient_count=patient_count,
        special_equipment=special_equipment,
    )


def is_supported_bridge_mode(value: str) -> bool:
    """Report whether the requested bridge mode is supported."""
    return value in SUPPORTED_BRIDGE_MODES


def classify_event_type(event_type: str) -> str:
    """Map a CoT event type to a supported bridge mode."""
    return _event_spec(event_type.strip())[0]


def _event_spec(event_type: str) -> tuple[str, Extractor]:
    """Return the bridge mode and extractor for a supported CoT event type."""
    try:
        return EVENT_SPECS[event_type]
    except KeyError as exc:
        raise ValueError(f"unsupported CoT event type: {event_type}") from exc


def mapping_from_event(root: Element, raw_payload: bytes) -> MappingResult:
    """Build a mapping result from a parsed CoT event element."""
    source_uid = root.attrib.get("uid", "").strip()
    if not source_uid:
        raise ValueError("missing CoT uid")

    event_type = root.attrib.get("type", "").strip()
    if not event_type:
        raise ValueError("missing CoT type")

    bridge_mode, extractor = _event_spec(event_type)
    normalized_request = extractor(root)

    return MappingResult(
        bridge_mode=bridge_mode,
        source_uid=source_uid,
        raw_payload=raw_payload,
        normalized_request=normalized_request,
    )


EVENT_SPECS: dict[str, tuple[str, Extractor]] = {
    "b-m-p-s-p-lxdr-maintenance": ("maintenance", _maintenance_detail_from_event),
    "b-m-p-s-p-lxdr-supply": ("supply", _supply_detail_from_event),
    "b-m-p-s-p-lxdr-casevac": ("casevac", _casevac_detail_from_event),
}
