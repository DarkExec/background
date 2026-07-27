#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
commit="$(git -C "$root" rev-parse HEAD)"
install="${DARKEXEC_BACKGROUND_INSTALL_ROOT:-${AGENTD_INSTALL_ROOT:-/opt/darkexec-background}}"
release="$install/releases/$commit"
bin_path="${DARKEXEC_BACKGROUND_BIN_PATH:-/usr/local/bin/darkexec-back}"
legacy_bin_path="${AGENTD_BIN_PATH:-/usr/local/bin/agentd}"
systemd_dir="${DARKEXEC_BACKGROUND_SYSTEMD_DIR:-${AGENTD_SYSTEMD_DIR:-/etc/systemd/system}}"

"$root/scripts/validate.sh"
mkdir -p "$install/releases" "$(dirname "$bin_path")" "$systemd_dir"
if [[ ! -d "$release" ]]; then
  git clone --quiet --no-local "$root" "$release"
  git -C "$release" checkout --quiet --detach "$commit"
fi
ln -sfn "$release" "$install/.current"
mv -Tf "$install/.current" "$install/current"
ln -sfn "$install/current/bin/darkexec-back" "$bin_path"
ln -sfn "$bin_path" "$legacy_bin_path"
for unit in darkexec-background@.service darkexec-background@.timer; do
  ln -sfn "$install/current/systemd/$unit" "$systemd_dir/$unit"
done

printf '{"commit":"%s","binPath":"%s","legacyBinPath":"%s","systemdDir":"%s","enabled":false}\n' \
  "$commit" "$bin_path" "$legacy_bin_path" "$systemd_dir"
