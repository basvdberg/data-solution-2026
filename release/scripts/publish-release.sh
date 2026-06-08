#!/usr/bin/env bash
# Create annotated tag and GitHub release for release/VERSION at the current commit (or COMMIT_SHA).
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

commit_sha="${COMMIT_SHA:-${GITHUB_SHA:-}}"
if [[ -z "$commit_sha" ]]; then
  commit_sha="$(git rev-parse HEAD)"
fi

version="$(git show "${commit_sha}:release/VERSION" 2>/dev/null | tr -d ' \r\n' || true)"
if [[ -z "$version" ]]; then
  echo "publish-release: no release/VERSION at ${commit_sha}; skipping."
  exit 0
fi
if [[ "$version" != v* ]]; then
  version="v${version}"
fi

if [[ "$version" =~ ^v([0-9]{4})\.([0-9]{2})\.([0-9]{2})\.[0-9]+$ ]]; then
  notes_path="release/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}/${BASH_REMATCH[3]}/${version}/notes.md"
else
  echo "publish-release: invalid version format ${version}; skipping."
  exit 0
fi

if [[ ! -f "$notes_path" ]]; then
  echo "publish-release: missing ${notes_path}; skipping GitHub release."
  exit 0
fi

echo "publish-release: version ${version} at ${commit_sha}"

if ! git rev-parse --verify "refs/tags/${version}" >/dev/null 2>&1; then
  git tag -a "$version" "$commit_sha" -m "Release ${version}"
  echo "publish-release: created tag ${version}"
else
  echo "publish-release: tag ${version} already exists"
fi

git push origin "refs/tags/${version}" 2>&1 || echo "publish-release: tag push skipped (may already exist on remote)"

if command -v gh >/dev/null 2>&1; then
  if gh release view "$version" >/dev/null 2>&1; then
    echo "publish-release: GitHub release ${version} already exists"
  else
    gh release create "$version" \
      --target "$commit_sha" \
      --title "Release ${version}" \
      --notes-file "$notes_path"
    echo "publish-release: created GitHub release ${version}"
  fi
else
  echo "publish-release: gh CLI not found; skipping GitHub release."
fi
