# DarkExec Background

This repository owns durable unattended dispatch from one declared event to at most one DarkExec run and one private terminal receipt. Start with one request route and retrieve deeper context only for a named unresolved decision.

## Request routing

- For job parsing, event identity, dispatch, terminalization, receipts, or recovery behavior, start in `bin/darkexec-background` and `scripts/test_background.py`.
- For owner-produced Watch projections or their privacy contract, start in `schemas/darkexec-background-projection.v1.schema.json`, `examples/projections/`, and `scripts/test_projection_contract.py`.
- For timers, services, installation, or disabled-by-default host bindings, start in `systemd/`, `scripts/install.sh`, and their assertions in `scripts/validate.sh`.

Start with one route. Add another only for a distinct unresolved decision.

## Working loop

1. Inspect the routed implementation, closest fixtures, and current repository state before broader documentation or history.
2. Name what local evidence leaves unresolved, then choose one context route below; continue without more documentation when no decision remains open.
3. Make the smallest Background-owned change and prove the exact job, projection, service, or installation claim at its native boundary.
4. For an authorized change, finish commit, publication, merge, canonical synchronization, installation when applicable, identity readback, cleanup, and concise handoff.

## Context routing

- For stable ownership, state transitions, concurrency, or the Watch boundary, read the relevant section of [Architecture](ARCHITECTURE.md).
- For credentials, prompt bodies, private receipts, filesystem access, or execution authority, read the relevant section of [Security](SECURITY.md).
- For accepted behavior and deterministic proof, read the relevant section of [Quality](docs-quality.md).
- For supported job definition and operator usage, read the relevant section of [README](README.md).

Do not preload all four documents. Follow another route only when its evidence can change the current decision.

## Boundaries

- Background owns durable background dispatch, not monitoring or business policy.
- Preserve one job, one event identity, and at most one DarkExec dispatch.
- Never store prompt bodies, credentials, private task transcripts, or target data in receipts.
- Terminalize timeout, signal, transport failure, launch failure, and DarkExec failure.
- Keep systemd installation disabled by default.

## Validation

Run `./scripts/validate.sh`.
