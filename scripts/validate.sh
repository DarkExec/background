#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for path in AGENTS.md ARCHITECTURE.md CONTRIBUTING.md LICENSE README.md SECURITY.md \
  bin/agentd docs-quality.md scripts/install.sh scripts/test_agentd.py \
  systemd/darkexec-agentd@.service systemd/darkexec-agentd@.timer; do
  [[ -s "$root/$path" ]] || {
    echo "missing required file: $path" >&2
    exit 1
  }
done

PYTHONDONTWRITEBYTECODE=1 python3 "$root/scripts/test_agentd.py"
bash -n "$root/scripts/install.sh" "$root/scripts/validate.sh"
verify_output=""
if ! verify_output="$(systemd-analyze verify \
  "$root/systemd/darkexec-agentd@.service" \
  "$root/systemd/darkexec-agentd@.timer" 2>&1)"; then
  unexpected="$(printf '%s\n' "$verify_output" |
    grep -Fv 'Command /usr/local/bin/agentd is not executable: No such file or directory' || true)"
  [[ -z "$unexpected" ]] || {
    printf '%s\n' "$verify_output" >&2
    exit 1
  }
  echo "systemd syntax passed; installed executable binding not present"
fi
git -C "$root" diff --check
echo "agentd validation passed"
