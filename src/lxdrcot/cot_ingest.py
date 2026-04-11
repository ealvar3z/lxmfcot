"""PyTAK ingest worker definitions."""

from __future__ import annotations

from typing import Any
from xml.etree.ElementTree import ParseError, fromstring

from .cot_emit import build_status_cot
from .cot_map import MappingResult, mapping_from_event
from .router_bridge import accept_mapping


def classify_payload(data: bytes) -> MappingResult:
    """Classify raw CoT XML into a supported bridge mode."""
    try:
        root = fromstring(data)
    except ParseError as exc:
        raise ValueError("invalid CoT XML") from exc

    if root.tag != "event":
        raise ValueError(f"unsupported CoT root element: {root.tag}")

    return mapping_from_event(root, data)


def build_bridge_rx_worker(pytak_module: Any, rx_queue: Any, tx_queue: Any, config: Any) -> Any:
    """Build the first real PyTAK RX worker for lxdrcot."""

    class BridgeRXWorker(pytak_module.QueueWorker):
        def __init__(self, queue: Any, tx_queue: Any, config: Any) -> None:
            super().__init__(queue, config)
            self.tx_queue = tx_queue

        async def handle_data(self, data: bytes) -> None:
            mapping = classify_payload(data)
            outcome = accept_mapping(mapping)
            event = build_status_cot(mapping.source_uid, outcome.status_event)
            await self.put_queue(event, self.tx_queue)

    return BridgeRXWorker(rx_queue, tx_queue, config)
