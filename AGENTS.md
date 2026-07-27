# DarkExec Background

Read `ARCHITECTURE.md` and `docs-quality.md` before changing this repository.

- Background owns durable background dispatch, not monitoring or business policy.
- Preserve one job, one event identity, and at most one DarkExec dispatch.
- Never store prompt bodies, credentials, private task transcripts, or target data in receipts.
- Terminalize timeout, signal, transport failure, and DarkExec failure.
- Keep systemd installation disabled by default.
- Run `./scripts/validate.sh`.
