# Antigravity to Antigravity IDE Migration Tool

A safe, robust, and automated command-line utility to migrate configurations, settings, extensions (plugins), and conversation history from the legacy VSCode-fork based **Antigravity** application to the new standalone **Antigravity IDE** desktop application.

Designed with high software engineering standards for open-source distribution.

## Key Features

1. **Automated Backup & Rollback**: Automatically creates a timestamped backup of target configuration files before modification. If any part of the migration fails, it performs a complete automatic rollback to restore settings to their original state.
2. **Settings Merge**: Parses and safely merges `settings.json` without overwriting existing settings specific to the new IDE version.
3. **Extensions Migration & Path Rewriting**: Copies all installed VSCode extensions physically, and merges/rewrites the `extensions.json` file to update absolute paths from `.antigravity` to `.antigravity-ide`.
4. **Protobuf Database Merging**: Merges SQLite global storage (`state.vscdb`) keys, utilizing Protobuf binary wire format concatenation to safely combine historical conversation lists without needing a schema file.
5. **Dry-Run Simulation**: Supports a `--dry-run` flag to preview copy operations and database mutations before writing them to disk.
6. **Workspace Sync**: Syncs all Gemini agent state files (conversations, brain snapshots, prompting configs) that are present in the old app but missing in the new one.

---

## Safety Requirements

> [!CAUTION]
> **Before running the migration, you MUST close both Antigravity and Antigravity IDE.**
> SQLite databases (`state.vscdb`) are loaded and cached in memory when the editor is active. Running this tool while the editor is running may lead to the editor overwriting your migrated database on exit, resulting in data loss.

---

## Installation & Prerequisites

This tool requires **Python 3.8+** with no external dependencies (uses standard library modules like `sqlite3`, `json`, `shutil`, `argparse`, and `logging`).

1. Clone or download the repository to your workspace.
2. Ensure you have python installed:
   ```bash
   python --version
   ```

---

## Usage

Run the tool using the command line:

### 1. Perform a Dry-Run Simulation (Highly Recommended)
Preview the actions without modifying any files:
```bash
python -m src.main --dry-run --verbose
```

### 2. Run the Standard Migration
Perform the full migration (creates backup automatically):
```bash
python -m src.main
```

### 3. Restore from a Backup
If you need to restore your settings from an automatically created backup:
```bash
python -m src.main --restore "C:\Users\<Username>\AppData\Roaming\Antigravity IDE\migration_backups\<timestamp>"
```

### 4. Command-Line Options
```text
options:
  -h, --help           show this help message and exit
  --dry-run            Simulate the migration without making any modifications to files or database.
  --no-backup          Skip automatic configuration backups before migration (not recommended).
  --restore RESTORE    Path to a backup directory to restore configurations from.
  -v, --verbose        Enable verbose debug logging in console.
```

---

## Project Architecture

- `src/config.py`: Resolves environment paths dynamically (handles Windows APPDATA and profile folders).
- `src/backup.py`: Handles automatic ZIP/directory backups and rollback routines.
- `src/file_handler.py`: Merges `settings.json`, copies extensions, rewrites paths in `extensions.json`, and synchronizes `.gemini` folder structures.
- `src/database.py`: Performs SQLite key insertion and Protobuf concatenation merges.
- `src/main.py`: Coordinates the migration CLI process, process checks, and error boundaries.

---

## Testing

Run unit tests to verify the migration logic under simulated directory structures:
```bash
python -m unittest tests/test_migration.py
```
