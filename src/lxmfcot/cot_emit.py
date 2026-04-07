"""TAK/CoT status emission helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from xml.etree.ElementTree import Element, SubElement, tostring


@dataclass(slots=True, frozen=True)
class StatusEvent:
    """Represents a bridge status outcome for later CoT emission."""

    status: str
    detail: str


def _cot_time(offset_seconds: int = 0) -> str:
    """Return a TAK-compatible UTC timestamp."""
    moment = datetime.now(UTC) + timedelta(seconds=offset_seconds)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_status_cot(source_uid: str, event: StatusEvent) -> bytes:
    """Build a minimal CoT status event for bridge results."""
    root = Element(
        "event",
        attrib={
            "version": "2.0",
            "type": "b-m-p-s-p-lxdr",
            "uid": f"lxmfcot-{source_uid}-{event.status}",
            "how": "m-g",
            "time": _cot_time(),
            "start": _cot_time(),
            "stale": _cot_time(60),
        },
    )
    SubElement(
        root,
        "point",
        attrib={
            "lat": "0.0",
            "lon": "0.0",
            "hae": "0",
            "ce": "9999999",
            "le": "9999999",
        },
    )
    detail = SubElement(root, "detail")
    SubElement(
        detail,
        "lxmfcot",
        attrib={
            "source_uid": source_uid,
            "status": event.status,
            "detail": event.detail,
        },
    )
    return tostring(root, encoding="utf-8")
