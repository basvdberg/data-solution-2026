#!/bin/sh
# Enable repository Git hooks that refresh Markdown TOCs and project structure on each commit.
set -e
cd "$(dirname "$0")/.."
git config core.hooksPath .githooks
echo "Configured core.hooksPath=.githooks for $(git rev-parse --show-toplevel)"
