#!/bin/bash
cd "$(dirname "$0")" || exit 1
echo "Running Damn Antigravity IDE Migrator (WSL2 Dry-Run)..."
python3 -m src.main --forwsl2 --dry-run --verbose "$@"
