#!/usr/bin/env bash
# Source from NAS deploy/automation scripts so git and docker work in non-interactive SSH.
# Non-interactive sshd sessions use PATH=/usr/bin:/bin only; ~/.profile is not loaded.

NAS_REMOTE_PATH="${HOME}/.local/bin:/opt/bin:/opt/sbin:/usr/bin:/bin:/usr/sbin:/sbin"
export PATH="${NAS_REMOTE_PATH}${PATH:+:${PATH}}"

# Container Station / Entware (deploy-infra-on-nas.sh also extends PATH)
export PATH="${PATH}:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:/share/CACHEDEV1_DATA/.qpkg/Entware/bin"
