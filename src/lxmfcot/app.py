"""Application wiring for lxmfcot."""

from __future__ import annotations

import asyncio
from typing import Any

from .config import default_section
from .cot_ingest import classify_payload
from .router_bridge import accept_mapping


def _import_pytak() -> Any:
    try:
        import pytak  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime dependency gate
        raise RuntimeError(
            "pytak is not installed. Pin it in pyproject.toml before running lxmfcot."
        ) from exc
    return pytak


class BridgeReceiver:
    """Minimal RX-side handler used by the first bridge loop."""

    def __init__(self, queue: Any) -> None:
        self.queue = queue

    async def run_once(self) -> None:
        data = await self.queue.get()
        mapping = classify_payload(data)
        _ = accept_mapping(mapping)


async def run() -> None:
    """Run the bridge tool."""
    pytak = _import_pytak()
    config = default_section()
    clitool = pytak.CLITool(config)
    await clitool.setup()
    receiver = BridgeReceiver(clitool.rx_queue)
    while True:
        await receiver.run_once()
        await asyncio.sleep(0)


def main() -> None:
    """CLI entrypoint."""
    asyncio.run(run())

