"""Local in-memory LXDR router sink for bridge handoff."""

from __future__ import annotations

from dataclasses import dataclass, field

from .lxdr_request import LXDRRequestContainer


@dataclass(slots=True)
class LocalLXDRRouter:
    """Tracks submitted LXDR requests locally."""

    _submitted: list[LXDRRequestContainer] = field(default_factory=list)

    def submit(self, req: LXDRRequestContainer) -> LXDRRequestContainer:
        """Store one local LXDR request submission."""
        self._submitted.append(req)
        return req

    def submitted_requests(self) -> list[LXDRRequestContainer]:
        """Return the current submitted requests snapshot."""
        return list(self._submitted)
