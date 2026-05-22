#!/bin/bash
cd "$(dirname "$0")" || exit 1
echo "Running Damn Antigravity IDE Migrator (WSL2)..."
echo "NOTE: Run the standard Windows migration (01_migrate.bat) first!"
python3 -m src.main --forwsl2 "$@"
