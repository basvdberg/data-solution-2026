#!/usr/bin/env bash
set -euo pipefail

cd ~/apps/data-solution-2026
git fetch --all --tags
git checkout main
git pull origin main
python -m pip install --upgrade pip
pip install -e .
docker compose up -d
python -m extractor_and_poller.poller --list

echo "NAS deploy completed."
