# Quality

A qualified Agentd event has:

- one valid job definition and one stable event identity;
- no overlapping event for the same job;
- at most one DarkExec dispatch;
- prompt transport over stdin and only a prompt digest in Agentd state;
- terminal timeout, signal, transport failure, DarkExec failure, or completion;
- executive and target task identities on successful completion;
- atomic private receipt and deterministic status readback; and
- no detector, business policy, notification, target secret, or automatic resume behavior.

Offline tests use a fake DarkExec executable. Live qualification additionally requires exact native
Codex App visibility and a terminal DarkExec receipt for a read-only target.
