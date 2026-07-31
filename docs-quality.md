# Quality

A qualified Background event has:

- one valid job definition and one stable event identity;
- no overlapping event for the same job;
- at most one DarkExec dispatch;
- prompt transport over stdin and only a prompt digest in Background state;
- unbounded execution by default, with terminal signal, transport failure, DarkExec failure, or
  completion and an explicit positive timeout only when a job opts into one; the systemd service
  template must retain `TimeoutStartSec=infinity`;
- executive and target task identities on successful completion;
- an explicit `terminalAt` on completed, failed, timed-out, and interrupted receipts;
- atomic private receipt and deterministic status readback; and
- no detector, business policy, notification, target secret, or automatic resume behavior.

Offline tests use a fake DarkExec executable. Live qualification additionally requires exact native
Codex App visibility and a terminal DarkExec receipt for a read-only target.
