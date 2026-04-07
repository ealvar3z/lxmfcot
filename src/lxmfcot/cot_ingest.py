"""PyTAK ingest worker definitions."""

from __future__ import annotations

from typing import Any

from .cot_emit import build_status_cot
from .cot_map import MappingResult
from .router_bridge import accept_mapping


def classify_payload(data: bytes) -> MappingResult:
    """Classify raw payload bytes into the current placeholder bridge mode."""
    # v0 keeps the ingest contract narrow. Real CoT parsing lands next.
    return MappingResult(
        bridge_mode="maintenance",
        source_uid="pending",
        raw_payload=data,
    )


def build_bridge_rx_worker(pytak_module: Any, rx_queue: Any, tx_queue: Any, config: Any) -> Any:
    """Build the first real PyTAK RX worker for lxmfcot."""

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
