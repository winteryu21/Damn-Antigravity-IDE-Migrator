#!/bin/bash
echo "Running Damn Antigravity IDE Migrator (WSL2 Dry-Run)..."
python3 -m src.main --forwsl2 --dry-run --verbose "$@"
