# lxmfcot

`lxmfcot` is a TAK/CoT bridge for `LXDR`.

The project exists to connect tactical TAK/CoT workflows to the `LXDR` protocol implemented from `Project ADRIAN`, without building a new network stack. TAK remains the transport and operator surface. `lxmfcot` handles the protocol boundary:

- ingest CoT from TAK via `PyTAK`
- classify supported logistics events
- map those events into valid `LXDR` request containers
- hand requests to a local `LXDR` router
- emit CoT status and synchronization updates back to TAK

The design is intentionally similar to the small TAK bridge pattern used by projects such as `aiscot`, `djicot`, `adsbcot`, and `aprscot`.

## Scope

`lxmfcot` is not:

- a custom network stack
- a replacement for TAK
- a replacement for `LXDR`
- the authority for protocol validity or router state

`lxmfcot` is:

- a thin integration layer between CoT and `LXDR`
- a `PyTAK` application with focused workers
- a bridge for a small, explicit set of logistics workflows

## Planned Bridge Loop

The smallest useful loop is:

1. Receive CoT from TAK using `PyTAK`.
2. Parse and classify the incoming event.
3. Map the event into one supported `LXDR` request.
4. Pass the request into the local `LXDR` router.
5. Emit CoT status back to TAK:
   - accepted
   - invalid
   - synchronized

## Initial Supported Requests

The first bridge targets should stay narrow:

- maintenance request
- supply request
- CASEVAC request

These are the best first mappings because they already exist in `LXDR v1`, have clear operational value, and are easy to explain in a demo.

## Architecture

Planned module shape:

- `commands`
  - CLI entrypoint
- `app`
  - `PyTAK` `CLITool` setup and worker registration
- `cot_ingest`
  - RX-side CoT worker
- `cot_emit`
  - TX-side CoT status emitter
- `cot_map`
  - CoT to `LXDR` and `LXDR` to CoT mapping logic
- `router_bridge`
  - local handoff into the `LXDR` router
- `config`
  - bridge-specific configuration

## Mapping Discipline

`lxmfcot` will be strict.

- It will only accept supported CoT event types.
- It will only map fields that are explicitly understood.
- It will reject or mark incomplete events that cannot satisfy required `LXDR` fields.
- It will not silently invent protocol data.

`LXDR` remains the authority for:

- request validity
- link framing
- synchronization semantics
- router state

## Relationship To LXDR

`LXDR` is the main protocol effort.

`lxmfcot` is the next integration layer on top of that baseline. It exists to make `LXDR` usable in a TAK-centered workflow for experimentation, demos, and operational prototyping.

## Status

This repository is in early implementation state.

The immediate next work is:

- define the first CoT event contracts
- define exact CoT to `LXDR` field mappings
- build the first working `PyTAK` application skeleton
- implement one end-to-end mapping, likely maintenance first

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
