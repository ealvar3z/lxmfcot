# SBOM

This file is the local, human-readable software bill of materials for `lxmfcot`.

It is not the machine-resolved dependency graph. That role belongs to:

- `pyproject.toml`
- `uv.lock`

This file exists to capture provenance and intent that lockfiles do not explain well.

## Policy

The project will prefer dependencies in this order:

1. GitHub source pinned to an exact commit
2. Vendored source with preserved upstream provenance
3. PyPI only when necessary, pinned tightly and justified

Every direct dependency will record:

- package name
- purpose
- source
- pinned version, tag, or commit
- license
- whether it is runtime, development, or optional
- any local modifications or vendoring notes

## Current Intended Direct Dependencies

### `pytak`

- Purpose: TAK/CoT transport client and worker framework
- Source: `https://github.com/snstac/pytak`
- Pin: `fa875a181bd724a7a841be2384677fc363ebbac5`
- License: Apache-2.0
- Scope: runtime
- Notes: primary dependency for RX/TX queue workers and `CLITool` integration

### `takproto`

- Purpose: TAK protobuf support, only if required by the bridge path
- Source: GitHub
- Pin: pending
- License: pending verification
- Scope: optional runtime
- Notes: do not add unless the first bridge loop actually requires protobuf TAK payload support

## Planned Generated Artifacts

These are expected to be derived from the declared and locked dependencies, not maintained by hand:

- `uv.lock`
- CI-generated SPDX or CycloneDX SBOM
- GitHub dependency graph export

## Review Rules

Before adding a dependency:

1. Verify the source repository.
2. Prefer an exact Git commit pin.
3. Record the dependency here.
4. Confirm the license.
5. Decide whether the dependency belongs in runtime or development only.
6. Ensure the dependency can be explained in one sentence.

## Status

This file is the initial local SBOM.

It will be updated whenever any additional direct dependency is introduced.
