#!/usr/bin/env bash
# Source from NAS deploy/automation scripts so git and docker work in non-interactive SSH.
# Non-interactive sshd sessions use PATH=/usr/bin:/bin only; ~/.profile is not loaded.

_nas_remote_path_add() {
  local dir=$1
  [ -n "$dir" ] || return 0
  case ":${NAS_REMOTE_PATH}:" in
    *:"${dir}":*) return 0 ;;
  esac
  NAS_REMOTE_PATH="${NAS_REMOTE_PATH}:${dir}"
}

NAS_REMOTE_PATH="${HOME}/.local/bin:/opt/bin:/opt/sbin:/usr/bin:/bin:/usr/sbin:/sbin"

# QNAP QGit (HTTPS remotes need git-remote-https; prefer SSH origin on NAS)
if [ -d /opt/QGit/libexec/git-core ]; then
  _nas_remote_path_add /opt/QGit/libexec/git-core
fi

# Container Station docker (CACHEDEV volume index varies per NAS)
for _cs_bin in /share/CACHEDEV*_DATA/.qpkg/container-station/bin; do
  if [ -x "${_cs_bin}/docker" ]; then
    _nas_remote_path_add "$_cs_bin"
    break
  fi
done

# Entware optional CLI tools
for _ew_bin in /share/CACHEDEV*_DATA/.qpkg/Entware/bin; do
  if [ -d "$_ew_bin" ]; then
    _nas_remote_path_add "$_ew_bin"
    break
  fi
done

export PATH="${NAS_REMOTE_PATH}${PATH:+:${PATH}}"
