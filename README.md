# Agentd

Agentd is a durable background-agent runner for
[DarkExec](https://github.com/DarkExec/darkexec) and Codex App.

It converts a scheduled or externally identified event into at most one DarkExec dispatch, then
stores a compact terminal receipt containing the visible native task identities.

## Ownership

Agentd owns:

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
  "promptFile": "/etc/darkexec-agentd/prompts/daily-read-only.txt",
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
agentd validate-job --job /etc/darkexec-agentd/daily-read-only.json
sudo agentd run --job /etc/darkexec-agentd/daily-read-only.json --json
sudo agentd status --job /etc/darkexec-agentd/daily-read-only.json --json
```

Without `--event-id`, Agentd derives a UTC epoch-aligned slot from `cadenceSeconds`. Repeated calls
in the same slot read the same receipt. External schedulers may supply a stable `--event-id`.

The installer places but does not enable the systemd template. Enabling a timer is a separate
operator decision.

## Alpha limits

- Linux and systemd are the initial target.
- DarkExec and a running Codex App must already be configured.
- Job definitions and prompt files are operator-managed.
- Calendar expressions, notification transports, and multi-host coordination are not included.

## Licence

Apache-2.0.
