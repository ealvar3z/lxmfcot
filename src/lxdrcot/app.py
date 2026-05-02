"""Application wiring for lxdrcot.
 Module shape:
    - commands
      - CLI entrypoint
    - app
      - PyTAK CLITool setup and worker registration
    - cot_ingest
      - RX-side CoT worker
    - cot_emit
      - TX-side CoT status emitter
    - cot_map
      - CoT to LXDR and LXDR to CoT mapping logic
    - router_bridge
      - local handoff into the LXDR router
    - config
      - bridge-specific configuration
"""


from __future__ import annotations

import asyncio
from typing import Any

from .config import default_section
from .cot_ingest import build_bridge_rx_worker
from .local_router import LocalLXDRRouter


def _import_pytak() -> Any:
    try:
        import pytak  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime dependency gate
        raise RuntimeError(
            "pytak is not installed. Pin it in pyproject.toml before running lxdrcot."
        ) from exc
    return pytak


def build_clitool(pytak_module: Any, config: Any) -> Any:
    """Create the bridge CLITool."""
    return pytak_module.CLITool(config)


async def run() -> None:
    """Run the bridge tool."""
    pytak = _import_pytak()
    config = default_section()
    router = LocalLXDRRouter()
    clitool = build_clitool(pytak, config)
    await clitool.setup()
    clitool.add_tasks(
        {
            build_bridge_rx_worker(
                pytak,
                clitool.rx_queue,
                clitool.tx_queue,
                config,
                router=router,
            )
        }
    )
    await clitool.run()


def main() -> None:
    """CLI entrypoint."""
    asyncio.run(run())
