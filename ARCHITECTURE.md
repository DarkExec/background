# Architecture

```text
systemd timer or external trigger
  -> one versioned job definition + cadence/event identity
  -> per-job nonblocking lock
  -> one idempotent darkexec dispatch
  -> App-visible executive and target tasks
  -> same-task Harness Ops closeout
  -> compact terminal Background receipt
```

Background uses DarkExec as its only Codex execution boundary. It does not connect to Codex App
directly. DarkExec owns task creation, exact App-list visibility, target closeout, and its full
receipt. Background stores only the identities and terminal fields needed to audit the background
trigger.

State defaults to `/var/lib/darkexec-background` with directories mode `0700` and receipt mode
`0600`.
One lock per job prevents overlapping events for that job. The same event fails closed if its target,
prompt digest, or harness mode changes.

Schema v1 definitions retain file-backed prompts. Schema v2 adds `promptMode: stdin` for
target-owned live events such as watchdog incidents and Discord messages. The prompt is hashed for
idempotency and passed directly to DarkExec; it is never written into the compact Background
receipt. Existing v1 definitions and invocations remain valid.

Schedulers own when to invoke Background. Targets own their code, tools, tests, proof, and operational
memory. Notification systems own external delivery.

## Watch projection

Background owns the versioned, sanitized projection that optional operator views consume. The
projection is a bounded operational envelope, not a transcript or a replacement for the private
receipt. It keeps admission, execution, verification, notification, and attention as independent
facts so a consumer cannot turn “the agent finished” into “the real job succeeded.”

Product, harness, and notification outputs remain separate bounded facts. Each output names its
owner, source field, observation time, and composition inputs. This lets an operator compare later
evidence with an earlier payload and see which component selected the notification fields without
asking Watch to diagnose the target system.

The initial contract is `schemas/darkexec-background-projection.v1.schema.json`. It is deliberately
transport-neutral: a local fixture, file exporter, or future asynchronous HTTPS publisher can emit
the same document. Background execution never waits for a projection consumer.
