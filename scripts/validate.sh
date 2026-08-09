#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for path in AGENTS.md ARCHITECTURE.md CONTRIBUTING.md LICENSE README.md SECURITY.md \
  bin/darkexec-background docs-quality.md scripts/install.sh scripts/test_background.py \
  schemas/darkexec-background-projection.v1.schema.json \
  examples/projections/gos-watchdog.json examples/projections/voiceze-discord.json \
  scripts/test_projection_contract.py \
  systemd/darkexec-background@.service systemd/darkexec-background@.timer; do
  [[ -s "$root/$path" ]] || {
    echo "missing required file: $path" >&2
    exit 1
  }
done

python3 - "$root/AGENTS.md" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1]).read_text()
headings = ["## Request routing", "## Working loop", "## Context routing", "## Boundaries", "## Validation"]
positions = [source.index(heading) for heading in headings]
assert positions == sorted(positions)
for route in ("bin/darkexec-background", "schemas/darkexec-background-projection.v1.schema.json", "systemd/"):
    assert route in source
for owner in ("[Architecture](ARCHITECTURE.md)", "[Security](SECURITY.md)", "[Quality](docs-quality.md)", "[README](README.md)"):
    assert owner in source
assert "Start with one route." in source
assert "Do not preload all four documents." in source
PY
grep -Fq '`AGENTS.md` owns request-to-implementation and unresolved-decision routing' "$root/ARCHITECTURE.md"

grep -Fqx 'TimeoutStartSec=infinity' "$root/systemd/darkexec-background@.service"

PYTHONDONTWRITEBYTECODE=1 python3 "$root/scripts/test_background.py"
PYTHONDONTWRITEBYTECODE=1 python3 "$root/scripts/test_projection_contract.py"
bash -n "$root/scripts/install.sh" "$root/scripts/validate.sh"
verify_output=""
if ! verify_output="$(systemd-analyze verify \
  "$root/systemd/darkexec-background@.service" \
  "$root/systemd/darkexec-background@.timer" 2>&1)"; then
  unexpected="$(printf '%s\n' "$verify_output" |
    grep -Fv 'Command /usr/local/bin/darkexec-background is not executable: No such file or directory' || true)"
  [[ -z "$unexpected" ]] || {
    printf '%s\n' "$verify_output" >&2
    exit 1
  }
  echo "systemd syntax passed; installed executable binding not present"
fi
git -C "$root" diff --check
echo "background validation passed"
