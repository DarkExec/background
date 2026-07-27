# DarkExec Background

DarkExec Background is a durable background-agent runner for
[DarkExec](https://github.com/DarkExec/darkexec) and Codex App.

It converts a scheduled or externally identified event into at most one DarkExec dispatch, then
stores a compact terminal receipt containing the visible native task identities.

## Ownership

Background owns:

- cadence-slot or caller-supplied event identity;
- per-job concurrency exclusion;
- one idempotent DarkExec dispatch;
- timeout and signal terminalization;
- atomic private receipts; and
- status readback.

It does not own monitoring, business policy, incident classification, notification delivery, target
secrets, model selection, or automatic task resumption.

## Job definition

```json
{
  "schemaVersion": 1,
  "id": "daily-read-only",
  "target": "/absolute/saved/codex/project",
  "promptFile": "/etc/darkexec-background/prompts/daily-read-only.txt",
  "cadenceSeconds": 86400,
  "readOnlyHarness": true,
  "timeoutSeconds": 900
}
```

Prompts are read from files and sent to DarkExec over stdin; they do not appear in process
arguments. Receipts store only the prompt digest.

## Use

```bash
./scripts/validate.sh
sudo ./scripts/install.sh
darkexec-back validate-job --job /etc/darkexec-background/daily-read-only.json
sudo darkexec-back run --job /etc/darkexec-background/daily-read-only.json --json
sudo darkexec-back status --job /etc/darkexec-background/daily-read-only.json --json
```

Without `--event-id`, Background derives a UTC epoch-aligned slot from `cadenceSeconds`. Repeated
calls in the same slot read the same receipt. External schedulers may supply a stable `--event-id`.

The alpha installer also provides `agentd` as a deprecated compatibility alias. New integrations
should use `darkexec-back`; the planned DarkExec CLI entrypoint is `darkexec back`.

The installer places but does not enable the systemd template. Enabling a timer is a separate
operator decision.

## Alpha limits

- Linux and systemd are the initial target.
- DarkExec and a running Codex App must already be configured.
- Job definitions and prompt files are operator-managed.
- Calendar expressions, notification transports, and multi-host coordination are not included.

## Licence

Apache-2.0.
