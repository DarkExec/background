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

## Optional Watch projection

`schemas/darkexec-background-projection.v1.schema.json` defines the bounded operational facts that a
read-only consumer such as DarkExec Watch may receive. The schema excludes raw prompts, transcripts,
tool arguments, credentials, target payloads, and arbitrary command output.

The projection includes bounded product, harness, and notification summaries with explicit field
provenance. It may identify native tasks, project roots, and private receipt references, but it does
not copy the private receipt or raw agent trace into Watch.

The two sanitized examples deliberately exercise different shapes:

- `examples/projections/gos-watchdog.json`: an incident-triggered agent completed while domain
  verification remained partial.
- `examples/projections/voiceze-discord.json`: a Discord event was deterministically suppressed, so
  no agent task was expected.

These examples are compatibility fixtures, not production records.

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

Event-driven owners use the additive v2 definition and supply each natural prompt on stdin:

```json
{
  "schemaVersion": 2,
  "id": "gos-watchdog",
  "target": "/srv/voice",
  "promptMode": "stdin",
  "cadenceSeconds": 1800,
  "readOnlyHarness": false,
  "timeoutSeconds": 3600
}
```

```bash
printf '%s' "$incident_prompt" |
  darkexec-background run \
    --job /etc/darkexec-background/gos-watchdog.json \
    --event-id gos-watchdog-<uuid> \
    --prompt-stdin \
    --json
```

V1 file-backed definitions remain unchanged. V2 is deliberately small: the target still owns event
detection, admission, prompt construction, verification, and notification.

## Use

```bash
./scripts/validate.sh
sudo ./scripts/install.sh
darkexec-background validate-job --job /etc/darkexec-background/daily-read-only.json
sudo darkexec-background run --job /etc/darkexec-background/daily-read-only.json --json
sudo darkexec-background status --job /etc/darkexec-background/daily-read-only.json --json
```

Without `--event-id`, Background derives a UTC epoch-aligned slot from `cadenceSeconds`. Repeated
calls in the same slot read the same receipt. External schedulers may supply a stable `--event-id`.

The standalone alpha executable is `darkexec-background`; the planned DarkExec umbrella CLI
entrypoint is `darkexec back`.

The installer places but does not enable the systemd template. Enabling a timer is a separate
operator decision.

## Alpha limits

- Linux and systemd are the initial target.
- DarkExec and a running Codex App must already be configured.
- Job definitions and prompt files are operator-managed.
- Calendar expressions, notification transports, and multi-host coordination are not included.

## Licence

Apache-2.0.
