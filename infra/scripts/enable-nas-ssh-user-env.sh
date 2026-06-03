#!/usr/bin/env bash
# One-time BasNAS admin step: allow ~/.ssh/environment for non-interactive SSH PATH.
# Requires sudo (administrator password on QNAP).
#
# Usage (on NAS, interactive):
#   bash infra/scripts/enable-nas-ssh-user-env.sh

set -euo pipefail

CFG=/etc/ssh/sshd_config

if [ ! -f "$CFG" ]; then
  echo "ERROR: ${CFG} not found." >&2
  exit 1
fi

if grep -q '^PermitUserEnvironment yes' "$CFG"; then
  echo "PermitUserEnvironment already enabled."
else
  echo "Enabling PermitUserEnvironment in ${CFG} (sudo required)..."
  sudo cp -p "$CFG" "${CFG}.bak.$(date +%Y%m%d%H%M%S)"
  if grep -q '^#PermitUserEnvironment' "$CFG"; then
    sudo sed -i 's/^#PermitUserEnvironment.*/PermitUserEnvironment yes/' "$CFG"
  elif grep -q '^PermitUserEnvironment' "$CFG"; then
    sudo sed -i 's/^PermitUserEnvironment.*/PermitUserEnvironment yes/' "$CFG"
  else
    printf '\nPermitUserEnvironment yes\n' | sudo tee -a "$CFG" >/dev/null
  fi
fi

echo "Restarting SSH service (existing sessions stay connected)..."
if [ -x /etc/init.d/sshd.sh ]; then
  sudo /etc/init.d/sshd.sh restart
elif command -v systemctl >/dev/null 2>&1; then
  sudo systemctl reload sshd || sudo systemctl restart sshd
else
  echo "WARN: could not restart sshd automatically; reload SSH from QNAP Control Panel." >&2
fi

echo "Done. Test from another machine: ssh bas@basnas 'git --version'"
