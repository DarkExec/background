#!/usr/bin/env python3
"""Deterministic Background contract tests with a fake DarkExec executable."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKGROUND = ROOT / "bin/darkexec-background"

FAKE_DARKEXEC = """#!/usr/bin/env python3
import json, os, pathlib, sys, time
count = pathlib.Path(os.environ["DARKEXEC_BACKGROUND_FAKE_COUNT"])
count.write_text(str(int(count.read_text() or "0") + 1))
prompt = sys.stdin.read()
if prompt == "SLOW":
    time.sleep(30)
if prompt == "DELAYED":
    time.sleep(0.2)
print(json.dumps({
    "status": "completed",
    "executive": {"threadId": "executive-visible"},
    "target": {
        "threadId": "target-visible",
        "harness": {"status": "completed"}
    }
}))
"""


def invoke(command: list[str], env: dict, prompt: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, input=prompt, capture_output=True, text=True, env=env, check=False)


def receipt_path(state: Path, job_id: str, event: str) -> Path:
    digest = hashlib.sha256(f"{job_id}\0{event}".encode()).hexdigest()
    return state / "receipts" / f"{digest}.json"


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        target = root / "target"
        target.mkdir()
        prompt = root / "prompt.txt"
        prompt.write_text("READ_ONLY")
        definition = root / "job.json"
        job = {
            "schemaVersion": 1,
            "id": "test-job",
            "target": str(target),
            "promptFile": str(prompt),
            "cadenceSeconds": 60,
            "readOnlyHarness": True,
            "timeoutSeconds": 2,
        }
        definition.write_text(json.dumps(job))
        fake = root / "darkexec"
        fake.write_text(FAKE_DARKEXEC)
        fake.chmod(0o755)
        count = root / "count"
        count.write_text("0")
        state = root / "state"
        env = {
            **os.environ,
            "DARKEXEC_BACKGROUND_STATE_ROOT": str(state),
            "DARKEXEC_BACKGROUND_DARKEXEC_BIN": str(fake),
            "DARKEXEC_BACKGROUND_FAKE_COUNT": str(count),
        }

        validate = invoke([str(BACKGROUND), "validate-job", "--job", str(definition)], env)
        assert validate.returncode == 0, validate.stderr
        first = invoke([
            str(BACKGROUND), "run", "--job", str(definition),
            "--event-id", "event-1", "--json",
        ], env)
        assert first.returncode == 0, first.stderr or first.stdout
        completed = json.loads(first.stdout)
        assert completed["status"] == "completed", completed
        assert completed["terminal"] is True
        assert completed["executiveThreadId"] == "executive-visible"
        assert completed["targetThreadId"] == "target-visible"
        assert completed["harnessStatus"] == "completed"
        assert "READ_ONLY" not in receipt_path(state, "test-job", "event-1").read_text()
        assert state.stat().st_mode & 0o777 == 0o700
        assert receipt_path(state, "test-job", "event-1").stat().st_mode & 0o777 == 0o600

        repeat = invoke([
            str(BACKGROUND), "run", "--job", str(definition),
            "--event-id", "event-1", "--json",
        ], env)
        assert repeat.returncode == 0
        assert json.loads(repeat.stdout)["createdAt"] == completed["createdAt"]
        assert count.read_text() == "1", count.read_text()

        status = invoke([
            str(BACKGROUND), "status", "--job", str(definition),
            "--event-id", "event-1", "--json",
        ], env)
        assert status.returncode == 0
        assert json.loads(status.stdout)["darkexecJobId"] == completed["darkexecJobId"]

        prompt.write_text("CHANGED")
        conflict = invoke([
            str(BACKGROUND), "run", "--job", str(definition),
            "--event-id", "event-1", "--json",
        ], env)
        assert conflict.returncode != 0
        assert "different target, prompt, or harness mode" in conflict.stderr

        prompt.write_text("SLOW")
        job["timeoutSeconds"] = 1
        definition.write_text(json.dumps(job))
        timed = invoke([
            str(BACKGROUND), "run", "--job", str(definition),
            "--event-id", "event-timeout", "--json",
        ], env)
        assert timed.returncode == 1, timed
        timed_receipt = json.loads(timed.stdout)
        assert timed_receipt["status"] == "failed" and timed_receipt["terminal"] is True
        assert timed_receipt["timedOut"] is True

        job["timeoutSeconds"] = 10
        definition.write_text(json.dumps(job))
        running = subprocess.Popen(
            [
                str(BACKGROUND), "run", "--job", str(definition),
                "--event-id", "event-running", "--json",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        running_receipt = receipt_path(state, "test-job", "event-running")
        for _ in range(100):
            if running_receipt.exists():
                break
            time.sleep(0.02)
        assert running_receipt.exists()
        busy = invoke([
            str(BACKGROUND), "run", "--job", str(definition),
            "--event-id", "event-overlap", "--json",
        ], env)
        assert busy.returncode == 75, busy
        assert json.loads(busy.stdout)["status"] == "busy"
        running.send_signal(signal.SIGTERM)
        stdout, stderr = running.communicate(timeout=5)
        assert running.returncode == 128 + signal.SIGTERM, (running.returncode, stdout, stderr)
        interrupted = json.loads(stdout)
        assert interrupted["status"] == "interrupted" and interrupted["terminal"] is True
        assert count.read_text() == "3", count.read_text()

        dynamic_definition = root / "dynamic-job.json"
        dynamic_job = {
            "schemaVersion": 2,
            "id": "dynamic-job",
            "target": str(target),
            "promptMode": "stdin",
            "cadenceSeconds": 60,
            "readOnlyHarness": False,
            "timeoutSeconds": 2,
        }
        dynamic_definition.write_text(json.dumps(dynamic_job))
        dynamic_validate = invoke(
            [str(BACKGROUND), "validate-job", "--job", str(dynamic_definition)],
            env,
        )
        assert dynamic_validate.returncode == 0, dynamic_validate.stderr
        dynamic_first = invoke([
            str(BACKGROUND), "run", "--job", str(dynamic_definition),
            "--event-id", "incident-1", "--prompt-stdin", "--json",
        ], env, "DYNAMIC INCIDENT")
        assert dynamic_first.returncode == 0, dynamic_first.stderr
        dynamic_receipt = json.loads(dynamic_first.stdout)
        assert dynamic_receipt["definitionSha256"]
        assert dynamic_receipt["runtimeVersion"] == "2"
        assert "DYNAMIC INCIDENT" not in receipt_path(state, "dynamic-job", "incident-1").read_text()
        dynamic_repeat = invoke([
            str(BACKGROUND), "run", "--job", str(dynamic_definition),
            "--event-id", "incident-1", "--prompt-stdin", "--json",
        ], env, "DYNAMIC INCIDENT")
        assert dynamic_repeat.returncode == 0
        assert count.read_text() == "4", count.read_text()
        dynamic_conflict = invoke([
            str(BACKGROUND), "run", "--job", str(dynamic_definition),
            "--event-id", "incident-1", "--prompt-stdin", "--json",
        ], env, "CHANGED INCIDENT")
        assert dynamic_conflict.returncode != 0
        dynamic_job["timeoutSeconds"] = 0
        dynamic_definition.write_text(json.dumps(dynamic_job))
        unbounded = invoke([
            str(BACKGROUND), "run", "--job", str(dynamic_definition),
            "--event-id", "incident-unbounded", "--prompt-stdin", "--json",
        ], env, "DELAYED")
        assert unbounded.returncode == 0, unbounded.stderr
        assert json.loads(unbounded.stdout)["status"] == "completed"
        missing_stdin = invoke([
            str(BACKGROUND), "run", "--job", str(dynamic_definition),
            "--event-id", "incident-2", "--json",
        ], env)
        assert missing_stdin.returncode != 0

    print(json.dumps({"status": "passed", "contracts": [
        "valid-job", "one-dispatch", "idempotent-event", "conflict-closed",
        "private-receipt", "status-readback", "timeout-terminalized",
        "concurrency-excluded", "signal-terminalized", "dynamic-stdin",
        "definition-digest", "v2-idempotency", "v2-conflict-closed",
        "unbounded-execution",
    ]}))


if __name__ == "__main__":
    main()
