# Architecture

```text
systemd timer or external trigger
  -> one job definition + cadence/event identity
  -> per-job nonblocking lock
  -> one idempotent darkexec dispatch
  -> App-visible executive and target tasks
  -> same-task Harness Ops closeout
  -> compact terminal agentd receipt
```

Agentd uses DarkExec as its only Codex execution boundary. It does not connect to Codex App directly.
DarkExec owns task creation, exact App-list visibility, target closeout, and its full receipt. Agentd
stores only the identities and terminal fields needed to audit the background trigger.

State defaults to `/var/lib/darkexec-agentd` with directories mode `0700` and receipt mode `0600`.
One lock per job prevents overlapping events for that job. The same event fails closed if its target,
prompt digest, or harness mode changes.

Schedulers own when to invoke Agentd. Targets own their code, tools, tests, proof, and operational
memory. Notification systems own external delivery.
