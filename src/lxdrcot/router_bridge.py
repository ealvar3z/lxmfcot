"""Bridge handoff into an LXDR router."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .cot_emit import StatusEvent
from .cot_map import CasevacRequest, MaintenanceRequest, MappingResult, SupplyRequest


@dataclass(slots=True, frozen=True)
class BridgeOutcome:
    """Represents the local bridge outcome."""

    accepted: bool
    status_event: StatusEvent


def accept_mapping(mapping: MappingResult) -> BridgeOutcome:
    """Accept a classified mapping into the local bridge flow."""
    detail = _bridge_detail(mapping)
    return BridgeOutcome(
        accepted=True,
        status_event=StatusEvent(
            status="accepted",
            detail=detail,
        ),
    )


def _bridge_detail(mapping: MappingResult) -> str:
    """Render a status detail string from the normalized request shape."""
    try:
        formatter = BRIDGE_DETAIL_FORMATTERS[mapping.bridge_mode]
    except KeyError:
        return f"{mapping.bridge_mode}:{mapping.source_uid}"
    return formatter(mapping)


def _require_maintenance_request(mapping: MappingResult) -> MaintenanceRequest:
    """Require a normalized maintenance request for maintenance mappings."""
    request = mapping.normalized_request
    if not isinstance(request, MaintenanceRequest):
        raise ValueError("missing normalized maintenance request")
    return request


def _require_supply_request(mapping: MappingResult) -> SupplyRequest:
    """Require a normalized supply request for supply mappings."""
    request = mapping.normalized_request
    if not isinstance(request, SupplyRequest):
        raise ValueError("missing normalized supply request")
    return request


def _require_casevac_request(mapping: MappingResult) -> CasevacRequest:
    """Require a normalized CASEVAC request for CASEVAC mappings."""
    request = mapping.normalized_request
    if not isinstance(request, CasevacRequest):
        raise ValueError("missing normalized casevac request")
    return request


def _format_maintenance_detail(mapping: MappingResult) -> str:
    request = _require_maintenance_request(mapping)
    return (
        f"maintenance:{request.source_uid}:"
        f"{request.request_priority}:{request.maintenance_support}:"
        f"{request.equipment_nomenclature}"
    )


def _format_supply_detail(mapping: MappingResult) -> str:
    request = _require_supply_request(mapping)
    return (
        f"supply:{request.source_uid}:"
        f"{request.request_priority}:{request.item_nomenclature}:"
        f"{request.quantity}:{request.needed_by}"
    )


def _format_casevac_detail(mapping: MappingResult) -> str:
    request = _require_casevac_request(mapping)
    return (
        f"casevac:{request.source_uid}:"
        f"{request.request_priority}:{request.pickup_location}:"
        f"{request.patient_count}:{request.special_equipment}"
    )


BRIDGE_DETAIL_FORMATTERS: dict[str, Callable[[MappingResult], str]] = {
    "maintenance": _format_maintenance_detail,
    "supply": _format_supply_detail,
    "casevac": _format_casevac_detail,
}
