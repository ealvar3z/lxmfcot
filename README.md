# lxdrcot

`lxdrcot` is a TAK/CoT bridge for `LXDR` (`Logistics eXchange Data Requirements`).

The project exists to connect tactical TAK/CoT workflows to the `LXDR` protocol implemented from `Project ADRIAN`, without building a new network stack. TAK remains the transport and operator surface. `lxdrcot` handles the protocol boundary:

- ingest CoT from TAK via `PyTAK`
- classify supported logistics events
- map those events into valid `LXDR` request containers
- hand requests to a local `LXDR` router
- emit CoT status and synchronization updates back to TAK

The design is intentionally similar to the small TAK bridge pattern used by projects such as `aiscot`, `djicot`, `adsbcot`, and `aprscot`.

## Emitted Bridge Status CoT

`lxdrcot` emits a bridge-status CoT event for each processed input.

Current status event shape:

- root element: `event`
- CoT type: `b-m-p-s-p-lxdr`
- UID format: `lxdrcot-{source_uid}-{status}`
- detail element: `<lxdrcot ... />`

Current emitted detail attributes:

- `source_uid`
    - the original inbound CoT UID when available
- `status`
    - one of:
        - `accepted`
        - `invalid`
- `detail`
    - a compact bridge summary
    - examples:
        - `maintenance:worker-unit:03:R3:FMTV`
        - `supply:supply-unit:04:water:12:2026-04-11T18:00:00Z`
        - `casevac:casevac-unit:01:18S UJ 22850 07080:2:hoist`
        - `missing maintenance issue_text`

Example emitted status event:

```xml
<event
  version="2.0"
  type="b-m-p-s-p-lxdr"
  uid="lxdrcot-worker-unit-accepted"
  how="m-g"
  time="2026-04-10T20:00:00Z"
  start="2026-04-10T20:00:00Z"
  stale="2026-04-10T20:01:00Z">
  <point lat="0.0" lon="0.0" hae="0" ce="9999999" le="9999999" />
  <detail>
    <lxdrcot
      source_uid="worker-unit"
      status="accepted"
      detail="maintenance:worker-unit:03:R3:FMTV" />
  </detail>
</event>
```

This status contract is intentionally narrow.

## Initial Supported Requests

The first bridge targets:

- maintenance request
- supply request
- CASEVAC request

## Python Environment

This repository uses `uv` for Python management.

It does not rely on the system Python and it does not rely on `pyenv`
for interpreter selection inside the repo.

Create the local virtual environment with the uv-managed Python 3.12
runtime:

```bash
PYENV_VERSION=3.14.3 uv venv --python /Users/eax/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/bin/python3.12
```

Run commands through the local environment:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests
```

or:

```bash
PYTHONPATH=src PYENV_VERSION=3.14.3 uv run python -m unittest discover -s tests
```

The repo-local `.venv` is the default Python for this project.
