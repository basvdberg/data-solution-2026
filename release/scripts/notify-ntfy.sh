#!/usr/bin/env bash
# Post a message to ntfy.sh (public topic). Used by GitHub Actions and shell deploy scripts.
# Usage: notify-ntfy.sh "Title" "Message" [priority] [click_url]
# Env: NTFY_TOPIC (default data-solution-2026-deploy), NTFY_BASE_URL (default https://ntfy.sh)
set -euo pipefail

title="${1:-Notification}"
message="${2:-}"
priority="${3:-default}"
click_url="${4:-}"

topic="${NTFY_TOPIC:-data-solution-2026-deploy}"
base="${NTFY_BASE_URL:-https://ntfy.sh}"
url="${base%/}/${topic}"

headers=(-H "Title: ${title}" -H "Priority: ${priority}")
if [[ -n "$click_url" ]]; then
  headers+=(-H "Click: ${click_url}")
fi

if [[ -z "$message" ]]; then
  message="$title"
fi

curl -fsS -X POST "${headers[@]}" -d "$message" "$url" >/dev/null || {
  echo "WARN: ntfy notification failed (topic=${topic})" >&2
  exit 0
}
